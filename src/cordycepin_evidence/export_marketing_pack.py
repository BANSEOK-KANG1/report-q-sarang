"""Export marketing_safe / research_only CSVs and marketing brief markdown."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any

from .utils import EVIDENCE_JSONL, EXPORT_DIR, ROOT, read_jsonl


FIELDS = [
    "record_id",
    "title",
    "year",
    "journal",
    "study_type",
    "evidence_strength",
    "species",
    "compound",
    "claim_category",
    "risk_flags",
    "relevance_to_product",
    "maps_to_market",
    "citation_status",
    "doi",
    "pmid",
    "url",
    "obsidian_path",
]


def _row(rec: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": rec.get("record_id"),
        "title": rec.get("title"),
        "year": rec.get("year"),
        "journal": rec.get("journal"),
        "study_type": rec.get("study_type"),
        "evidence_strength": rec.get("evidence_strength"),
        "species": rec.get("species"),
        "compound": rec.get("compound"),
        "claim_category": rec.get("claim_category"),
        "risk_flags": "|".join(rec.get("risk_flags") or []),
        "relevance_to_product": rec.get("relevance_to_product"),
        "maps_to_market": rec.get("maps_to_market"),
        "citation_status": rec.get("citation_status"),
        "doi": rec.get("doi"),
        "pmid": rec.get("pmid"),
        "url": rec.get("url"),
        "obsidian_path": rec.get("obsidian_path"),
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _one_liner(rec: dict[str, Any]) -> str:
    st = rec.get("study_type") or "unclear"
    cat = rec.get("claim_category") or "other"
    return f"{st} study touching {cat} endpoints (auto-tagged; verify before use)."


def write_brief(records: list[dict[str, Any]]) -> Path:
    safe = [
        r
        for r in records
        if r.get("citation_status") == "approved"
        and r.get("maps_to_market") == "KR_liquor_context"
    ]
    # Seed objective context cards from high-quality research_only for internal brief
    context = [
        r
        for r in records
        if r.get("priority_review")
        and r.get("relevance_to_product") in ("direct", "partial")
        and "species_mismatch" not in (r.get("risk_flags") or [])
    ][:15]

    lines = [
        "# Marketing Evidence Brief — 제왕충초 × 코디세핀",
        "",
        f"_Generated: {date.today().isoformat()}_",
        "",
        "> 제왕충초 담금주는 **주류**입니다. 아래 내용은 효능 광고 승인이 아닙니다.",
        "> 소비자 카피는 법무 검토 후 `citation_status=approved` + `KR_liquor_context`만 사용하세요.",
        "",
        "## 사용 가능 톤 (원칙)",
        "",
        "- 코디세핀(cordycepin)은 *Cordyceps*속 균류에서 연구되는 성분이다.",
        "- 관련 연구가 학술 문헌에 존재한다 (특정 질병 치료 효과와 무관).",
        "- “FDA 승인”, “식약처 효능 인정(담금주)”, “항암/치료/예방” 표현 금지.",
        "",
        "## Approved liquor-context citations",
        "",
    ]
    if not safe:
        lines.append("_아직 승인된 `KR_liquor_context` 레코드가 없습니다. 검수 후 `evidence.jsonl`에서 승격하세요._")
        lines.append("")
    else:
        for r in safe:
            lines.append(f"### {r.get('year')} — {r.get('title')}")
            lines.append(f"- Strength: `{r.get('evidence_strength')}` | Type: `{r.get('study_type')}`")
            lines.append(f"- DOI: {r.get('doi') or '—'} | PMID: {r.get('pmid') or '—'}")
            lines.append(f"- Allowed: {r.get('claim_text_allowed') or 'Objective ingredient / research-existence language only.'}")
            lines.append(f"- Prohibited: {r.get('claim_text_prohibited') or 'Any disease / efficacy claim.'}")
            lines.append("")

    lines.extend(
        [
            "## Priority review queue (internal — not for ads)",
            "",
            "다음 항목은 자동 우선 검수 후보입니다. 광고에 바로 쓰지 마세요.",
            "",
        ]
    )
    for r in context:
        lines.append(f"- **{r.get('year')}** [{r.get('study_type')}/{r.get('evidence_strength')}] {r.get('title')}")
        lines.append(f"  - {_one_liner(r)}")
        lines.append(f"  - flags: {', '.join(r.get('risk_flags') or []) or 'none'}")
        lines.append(f"  - link: {r.get('url') or r.get('doi') or '—'}")
        lines.append("")

    lines.extend(
        [
            "## Stats snapshot",
            "",
            f"- Total normalized records: **{len(records)}**",
            f"- research_only: **{sum(1 for r in records if r.get('maps_to_market')=='research_only')}**",
            f"- needs_legal_review: **{sum(1 for r in records if r.get('citation_status')=='needs_legal_review')}**",
            f"- approved liquor-context: **{len(safe)}**",
            "",
            "## See also",
            "",
            "- [PROCESS.md](PROCESS.md)",
            "- [COMPLIANCE.md](COMPLIANCE.md)",
            "",
        ]
    )

    path = ROOT / "docs" / "MARKETING_EVIDENCE_BRIEF.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[export] brief -> {path}")
    return path


def export_marketing_pack() -> None:
    records = read_jsonl(EVIDENCE_JSONL)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    safe = [
        _row(r)
        for r in records
        if r.get("citation_status") == "approved"
        and r.get("maps_to_market") == "KR_liquor_context"
    ]
    research = [
        _row(r)
        for r in records
        if r.get("maps_to_market") == "research_only"
        or r.get("citation_status") != "approved"
    ]

    _write_csv(EXPORT_DIR / "marketing_safe.csv", safe)
    _write_csv(EXPORT_DIR / "research_only.csv", research)
    write_brief(records)
    print(f"[export] marketing_safe={len(safe)} research_only={len(research)}")


if __name__ == "__main__":
    export_marketing_pack()
