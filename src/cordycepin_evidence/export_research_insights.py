"""Generate per-paper research insight pages (Korean summaries + English abstract)."""

from __future__ import annotations

import csv
import json
import re
from datetime import date
from html import unescape
from pathlib import Path
from typing import Any

import yaml

from .utils import EVIDENCE_JSONL, EXPORT_DIR, ROOT, load_yaml, read_jsonl, slugify, vault_path

from .fetch_paper_visuals import fetch_visuals_for_record

CONTENT_DIR = ROOT / "content" / "research"
WEB_CONTENT_DIR = ROOT / "web" / "content" / "research"
VAULT_INSIGHTS = "15_Research_Insights"

STUDY_TYPE_KO: dict[str, str] = {
    "rct": "무작위 대조 시험(RCT)",
    "observational_human": "관찰 연구(인간)",
    "systematic_review": "체계적 문헌고찰",
    "meta_analysis": "메타분석",
    "animal": "동물·세포 실험(전임상)",
    "in_vitro": "시험관(in vitro) 연구",
    "review_narrative": "서술적 리뷰",
    "case_report": "증례 보고",
    "unclear": "연구 유형 불명",
}

EVIDENCE_KO: dict[str, str] = {
    "A_human_RCT": "인간 RCT",
    "B_human_observational": "인간 관찰 연구",
    "C_animal": "동물/세포 실험",
    "D_in_vitro": "시험관 연구",
    "E_review": "리뷰·고찰",
    "F_review_only": "리뷰·고찰",
}

SPECIES_KO: dict[str, str] = {
    "Cordyceps_militaris": "Cordyceps militaris (동충하초)",
    "unclear": "균종 미특정",
}


def _clean(text: str) -> str:
    t = unescape(text or "")
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _parse_abstract_sections(abstract: str) -> dict[str, str]:
    """Split Europe PMC / PubMed structured abstracts."""
    raw = abstract or ""
    sections: dict[str, str] = {}
    parts = re.split(
        r"<h4>\s*(Background|Methods|Results|Conclusions?|Objective|Purpose)\s*</h4>",
        raw,
        flags=re.I,
    )
    if len(parts) > 1:
        i = 1
        while i + 1 < len(parts):
            key = parts[i].strip().lower()
            body = _clean(parts[i + 1])
            if body:
                sections[key.rstrip("s")] = body
            i += 2
    if not sections:
        plain = _clean(raw)
        if plain:
            sections["summary"] = plain
    return sections


def _title_blocked(title: str, cfg: dict[str, Any]) -> bool:
    t = _clean(title).lower()
    return any(k.lower() in t for k in cfg.get("exclude_title_keywords") or [])


def _title_preference(title: str, cfg: dict[str, Any]) -> int:
    t = _clean(title).lower()
    prefs = cfg.get("prefer_title_keywords") or []
    return sum(1 for k in prefs if k.lower() in t)


def _rank_record(r: dict[str, Any], cfg: dict[str, Any]) -> tuple:
    title = _clean(r.get("title") or "")
    if _title_blocked(title, cfg):
        return (99, 0, 0, 0)
    flags = r.get("risk_flags") or []
    disease = 1 if "disease_language" in flags else 0
    priority = 0 if r.get("priority_review") else 1
    approved = 0 if (
        r.get("citation_status") == "approved"
        and r.get("maps_to_market") == "KR_liquor_context"
    ) else 1
    pref = -_title_preference(title, cfg)
    year = -(r.get("year") or 0)
    abstract_ok = 0 if (r.get("abstract") or "").strip() else 1
    study_rank = {
        "systematic_review": 0,
        "meta_analysis": 0,
        "review_narrative": 1,
        "rct": 2,
        "observational_human": 3,
        "animal": 4,
        "in_vitro": 5,
    }.get(r.get("study_type") or "", 6)
    return (priority, approved, disease, abstract_ok, study_rank, pref, year)


def _select_records(records: list[dict[str, Any]], cfg: dict[str, Any]) -> list[dict[str, Any]]:
    pool: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    for r in records:
        if not (r.get("abstract") or "").strip():
            continue
        title_key = _clean(r.get("title") or "").lower()[:80]
        if title_key in seen_titles:
            continue
        if _title_blocked(_clean(r.get("title") or ""), cfg):
            continue
        include = False
        if cfg.get("include_priority_review") and r.get("priority_review"):
            include = True
        if (
            cfg.get("include_approved_liquor")
            and r.get("citation_status") == "approved"
            and r.get("maps_to_market") == "KR_liquor_context"
        ):
            include = True
        if r.get("relevance_to_product") in ("direct", "partial") and _title_preference(
            r.get("title") or "", cfg
        ) >= 2:
            include = True
        if include:
            seen_titles.add(title_key)
            pool.append(r)

    pool.sort(key=lambda r: _rank_record(r, cfg))
    limit = int(cfg.get("max_insights") or 20)
    return pool[:limit]


def _slug_for(r: dict[str, Any]) -> str:
    base = slugify(_clean(r.get("title") or "paper"), max_len=48)
    year = r.get("year") or ""
    pmid = (r.get("pmid") or "")[-6:]
    return f"{base}-{year}-{pmid}".strip("-")


def _authors_line(authors: list[str]) -> str:
    if not authors:
        return "저자 정보 없음"
    if len(authors) <= 3:
        return ", ".join(authors)
    return f"{authors[0]} 외 {len(authors) - 1}명"


def _insight_note(r: dict[str, Any]) -> str:
    st = r.get("study_type") or "unclear"
    ev = r.get("evidence_strength") or ""
    species = SPECIES_KO.get(r.get("species") or "", r.get("species") or "미확인")
    compound = r.get("compound") or "코디세핀·추출물"
    flags = r.get("risk_flags") or []

    lines = [
        "### 전문가 메모",
        "",
        f"- **연구 수준:** {EVIDENCE_KO.get(ev, ev)} · {STUDY_TYPE_KO.get(st, st)}",
        f"- **대상:** {species} / {compound}",
        f"- **제품 연관성:** {r.get('relevance_to_product') or 'unclear'}",
    ]
    if "preclinical_only" in flags:
        lines.append(
            "- **해석 주의:** 전임상(동물·세포) 결과는 인간 섭취·담금주 맥락으로 직접 확장하기 어렵습니다."
        )
    if "disease_language" in flags:
        lines.append(
            "- **해석 주의:** 원문에 질병·치료 관련 서술이 포함되어 있습니다. "
            "본 요약은 성분·균류 **연구 맥락**만 중립적으로 정리했습니다."
        )
    if st in ("systematic_review", "review_narrative", "meta_analysis"):
        lines.append(
            "- **인사이트:** 여러 연구를 종합한 고찰이므로, 개별 실험의 질·편향을 "
            "원문 표/부록에서 확인하는 것이 좋습니다."
        )
    elif st == "rct":
        lines.append(
            "- **인사이트:** 인간 RCT는 상대적으로 높은 근거 수준이나, "
            "시료·용량·기간이 제왕충초 담금주와 동일하지 않을 수 있습니다."
        )
    elif st in ("animal", "in_vitro"):
        lines.append(
            "- **인사이트:** 배양·생산·기초 메커니즘 연구로 읽는 것이 적절합니다. "
            "소비자 효능 주장 근거로 사용할 수 없습니다."
        )
    else:
        lines.append(
            "- **인사이트:** 원문의 연구 설계·표본·통계를 확인한 뒤 인용하세요."
        )
    lines.append("")
    return "\n".join(lines)


def _section_ko(key: str, text: str) -> str:
    labels = {
        "background": "연구 배경",
        "objective": "연구 목적",
        "purpose": "연구 목적",
        "method": "연구 방법",
        "methods": "연구 방법",
        "result": "주요 결과",
        "results": "주요 결과",
        "conclusion": "저자 결론",
        "conclusions": "저자 결론",
        "summary": "초록 요지",
    }
    label = labels.get(key, key)
    return f"### {label}\n\n{text}\n"


def _korean_summary(r: dict[str, Any], sections: dict[str, str]) -> str:
    """Structured Korean framing — editorial summary, not word-for-word translation."""
    title = _clean(r.get("title") or "")
    year = r.get("year") or ""
    st_ko = STUDY_TYPE_KO.get(r.get("study_type") or "", "연구")
    species = SPECIES_KO.get(r.get("species") or "", r.get("species") or "Cordyceps spp.")

    intro = (
        f"**{year}년** 발표된 「{_clean(title)}」은(는) "
        f"**{species}** 및 **코디세핀** 관련 {st_ko}입니다. "
        "아래는 원문 초록을 바탕으로 한 **중립적 요약**이며, "
        "제품 효능·효과를 의미하지 않습니다."
    )
    parts = ["## 한국어 요약", "", intro, ""]
    order = ("background", "objective", "purpose", "methods", "method", "results", "result", "conclusions", "conclusion", "summary")
    used: set[str] = set()
    for key in order:
        if key in sections and key not in used:
            parts.append(_section_ko(key, sections[key]))
            used.add(key)
    for key, text in sections.items():
        if key not in used:
            parts.append(_section_ko(key, text))
    parts.append(_insight_note(r))
    return "\n".join(parts)


def _bibliography(r: dict[str, Any]) -> str:
    doi = r.get("doi") or ""
    pmid = r.get("pmid") or ""
    url = r.get("url") or (f"https://doi.org/{doi}" if doi else "")
    lines = [
        "## 출처 · 원문",
        "",
        f"- **제목:** {_clean(r.get('title') or '')}",
        f"- **저자:** {_authors_line(r.get('authors') or [])}",
        f"- **연도:** {r.get('year') or ''}",
    ]
    if r.get("journal"):
        lines.append(f"- **저널:** {r['journal']}")
    if doi:
        lines.append(f"- **DOI:** [{doi}](https://doi.org/{doi})")
    if pmid:
        lines.append(f"- **PMID:** [{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
    if url:
        lines.append(f"- **링크:** {url}")
    lines.append("")
    return "\n".join(lines)


def _english_abstract(r: dict[str, Any], sections: dict[str, str]) -> str:
    lines = ["## 원문 초록 (English)", ""]
    if sections:
        for key in ("background", "methods", "results", "conclusions", "summary"):
            if key in sections:
                lines.append(f"**{key.title()}** — {sections[key]}")
                lines.append("")
    else:
        lines.append(_clean(r.get("abstract") or ""))
        lines.append("")
    return "\n".join(lines)


def _description(r: dict[str, Any]) -> str:
    st = STUDY_TYPE_KO.get(r.get("study_type") or "", "연구")
    year = r.get("year") or ""
    species = SPECIES_KO.get(r.get("species") or "", "Cordyceps")
    return f"{year} · {st} · {species} — 코디세핀·제왕충초 관련 학술 문헌 전문 요약 (교육용)"


def _frontmatter(
    r: dict[str, Any],
    slug: str,
    cfg: dict[str, Any],
    visual: dict[str, Any] | None = None,
) -> str:
    flags = r.get("risk_flags") or []
    data = {
        "title": _clean(r.get("title") or ""),
        "title_ko": _clean(r.get("title") or ""),
        "slug": slug,
        "record_id": r.get("record_id"),
        "date": date.today().isoformat(),
        "year": r.get("year"),
        "authors": r.get("authors") or [],
        "doi": r.get("doi") or "",
        "pmid": r.get("pmid") or "",
        "pmcid": (visual or {}).get("pmcid") or r.get("pmcid") or "",
        "url": r.get("url") or "",
        "study_type": r.get("study_type"),
        "evidence_strength": r.get("evidence_strength"),
        "species": r.get("species"),
        "compound": r.get("compound"),
        "claim_category": r.get("claim_category"),
        "risk_flags": flags,
        "citation_status": r.get("citation_status"),
        "maps_to_market": r.get("maps_to_market"),
        "description": _description(r),
        "category": "research",
        "compliance": "research_education_only",
        "no_disease_claims": True,
        "no_efficacy_claims": True,
        "status": "published",
        "tags": ["research", "cordycepin", "evidence", "제왕충초"],
        "generated": date.today().isoformat(),
    }
    if visual:
        data["visuals"] = visual.get("figures") or []
        data["api_meta"] = {
            "keywords": visual.get("keywords") or [],
            "mesh_terms": visual.get("mesh_terms") or [],
            "concepts": visual.get("concepts") or [],
            "cited_by_count": visual.get("cited_by_count"),
            "reference_count": visual.get("reference_count"),
            "publisher": visual.get("publisher") or "",
            "journal": visual.get("journal") or "",
            "oa_status": visual.get("oa_status") or "",
            "oa_url": visual.get("oa_url") or "",
            "apis": visual.get("apis") or {},
            "fetched_at": visual.get("fetched_at") or "",
        }
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{body}\n---\n"


def _write_insight(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def export_research_insights() -> int:
    cfg = load_yaml("research_insights.yaml")
    records = read_jsonl(EVIDENCE_JSONL)
    selected = _select_records(records, cfg)
    if not selected:
        print("[research] no records matched filters")
        return 0

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    WEB_CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    vault = vault_path()
    vault_insights = vault / VAULT_INSIGHTS
    vault_insights.mkdir(parents=True, exist_ok=True)

    index_rows: list[dict[str, str]] = []
    disclaimer = (cfg.get("disclaimer") or "").strip()
    fetch_visuals = cfg.get("fetch_visuals", True)
    visual_manifests: dict[str, dict[str, Any]] = {}

    for r in selected:
        slug = _slug_for(r)
        visual: dict[str, Any] | None = None
        if fetch_visuals:
            print(f"[research] fetching visuals for {slug}")
            visual = fetch_visuals_for_record(r, slug)
            visual_manifests[slug] = visual
        sections = _parse_abstract_sections(r.get("abstract") or "")
        fm = _frontmatter(r, slug, cfg, visual)
        body_parts = [
            _korean_summary(r, sections),
            _bibliography(r),
            _english_abstract(r, sections),
        ]
        if disclaimer:
            body_parts.append(f"---\n\n*{disclaimer}*")
        md = fm + "\n" + "\n".join(body_parts) + "\n"

        out = CONTENT_DIR / f"{slug}.md"
        _write_insight(out, md)
        _write_insight(WEB_CONTENT_DIR / f"{slug}.md", md)
        _write_insight(vault_insights / f"{slug}.md", md)

        index_rows.append(
            {
                "slug": slug,
                "title": _clean(r.get("title") or ""),
                "year": str(r.get("year") or ""),
                "study_type": r.get("study_type") or "",
                "evidence_strength": r.get("evidence_strength") or "",
                "doi": r.get("doi") or "",
                "path": str(out.relative_to(ROOT)),
            }
        )

    index_path = EXPORT_DIR / "research_insights_index.csv"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "slug",
                "title",
                "year",
                "study_type",
                "evidence_strength",
                "doi",
                "path",
            ],
        )
        w.writeheader()
        w.writerows(index_rows)

    if visual_manifests:
        from .fetch_paper_visuals import VISUALS_JSON

        VISUALS_JSON.parent.mkdir(parents=True, exist_ok=True)
        VISUALS_JSON.write_text(
            json.dumps(visual_manifests, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        fig_count = sum(len(m.get("figures") or []) for m in visual_manifests.values())
        print(f"[research] visuals: {fig_count} figures -> {VISUALS_JSON}")

    print(f"[research] wrote {len(selected)} insight pages -> {CONTENT_DIR}")
    print(f"[research] index -> {index_path}")
    return len(selected)


def refresh_research_visuals() -> int:
    """Re-fetch API visuals for existing research markdown pages."""
    import yaml as yaml_lib

    from .fetch_paper_visuals import VISUALS_JSON, fetch_visuals_for_record

    records = {r["record_id"]: r for r in read_jsonl(EVIDENCE_JSONL)}
    visual_manifests: dict[str, dict[str, Any]] = {}
    updated = 0

    for path in sorted(CONTENT_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            continue
        parts = raw.split("---", 2)
        if len(parts) < 3:
            continue
        fm = yaml_lib.safe_load(parts[1]) or {}
        slug = fm.get("slug") or path.stem
        record = records.get(fm.get("record_id") or "")
        if not record:
            continue
        print(f"[research-visuals] {slug}")
        visual = fetch_visuals_for_record(record, slug)
        visual_manifests[slug] = visual
        cfg = load_yaml("research_insights.yaml")
        new_fm = _frontmatter(record, slug, cfg, visual)
        path.write_text(new_fm + "\n" + parts[2].lstrip("\n"), encoding="utf-8")
        web_path = WEB_CONTENT_DIR / path.name
        web_path.write_text(new_fm + "\n" + parts[2].lstrip("\n"), encoding="utf-8")
        (vault_path() / VAULT_INSIGHTS / path.name).write_text(
            new_fm + "\n" + parts[2].lstrip("\n"), encoding="utf-8"
        )
        updated += 1

    if visual_manifests:
        VISUALS_JSON.write_text(
            json.dumps(visual_manifests, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    print(f"[research-visuals] updated {updated} pages")
    return updated
