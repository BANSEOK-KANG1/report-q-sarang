"""Sync evidence records to Obsidian vault as Markdown + YAML frontmatter."""

from __future__ import annotations

from typing import Any

import yaml

from .utils import EVIDENCE_JSONL, ensure_dirs, read_jsonl, slugify, vault_path, write_jsonl


def _frontmatter(rec: dict[str, Any]) -> str:
    # YAML-safe subset for Dataview
    data = {
        "record_id": rec.get("record_id"),
        "title": rec.get("title"),
        "authors": rec.get("authors") or [],
        "year": rec.get("year"),
        "journal": rec.get("journal"),
        "doi": rec.get("doi"),
        "pmid": rec.get("pmid"),
        "url": rec.get("url"),
        "track": rec.get("track"),
        "compound": rec.get("compound"),
        "species": rec.get("species"),
        "study_type": rec.get("study_type"),
        "evidence_strength": rec.get("evidence_strength"),
        "relevance_to_product": rec.get("relevance_to_product"),
        "claim_category": rec.get("claim_category"),
        "risk_flags": rec.get("risk_flags") or [],
        "maps_to_market": rec.get("maps_to_market"),
        "citation_status": rec.get("citation_status"),
        "priority_review": rec.get("priority_review"),
        "jurisdiction_caveats": rec.get("jurisdiction_caveats") or [],
        "source_apis": rec.get("source_apis") or [],
        "full_text_available": rec.get("full_text_available"),
        "tags": [
            "evidence",
            f"status/{rec.get('citation_status') or 'candidate'}",
            f"study/{rec.get('study_type') or 'unclear'}",
            f"market/{rec.get('maps_to_market') or 'research_only'}",
        ],
    }
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{body}\n---\n"


def _note_body(rec: dict[str, Any]) -> str:
    abs_text = (rec.get("abstract") or "").strip() or "_No abstract_"
    flags = ", ".join(rec.get("risk_flags") or []) or "none"
    return f"""# {rec.get('title') or 'Untitled'}

## Summary fields
- **Year:** {rec.get('year') or '—'}
- **Study type:** {rec.get('study_type')}
- **Evidence strength:** {rec.get('evidence_strength')}
- **Species:** {rec.get('species')}
- **Compound:** {rec.get('compound')}
- **Claim category:** {rec.get('claim_category')}
- **Risk flags:** {flags}
- **Maps to market:** {rec.get('maps_to_market')}
- **Citation status:** {rec.get('citation_status')}
- **DOI:** {rec.get('doi') or '—'}
- **PMID:** {rec.get('pmid') or '—'}
- **URL:** {rec.get('url') or '—'}

## Abstract
{abs_text}

## Relevance notes
{rec.get('relevance_notes') or '_n/a_'}

## Compliance
- Product context: Q-Sarang 제왕충초 **liquor** (not HFF).
- Do not convert this note into disease / efficacy advertising copy without legal approval.
- See [[COMPLIANCE]] and `docs/COMPLIANCE.md`.

## Allowed / prohibited claim drafts
- **Allowed (if approved):** {rec.get('claim_text_allowed') or '_empty_'}
- **Prohibited phrasing:** {rec.get('claim_text_prohibited') or '_empty_'}
"""


def sync_obsidian() -> int:
    ensure_dirs()
    vault = vault_path()
    evidence_dir = vault / "10_Evidence"
    safe_dir = vault / "30_Marketing_Safe"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    safe_dir.mkdir(parents=True, exist_ok=True)

    # Replace auto-generated evidence notes to avoid stale slug collisions
    for p in evidence_dir.glob("*.md"):
        p.unlink()
    for p in safe_dir.glob("*.md"):
        if p.name.startswith("_"):
            continue
        p.unlink()

    records = read_jsonl(EVIDENCE_JSONL)
    count = 0
    used_names: set[str] = set()
    for rec in records:
        year = rec.get("year") or "nodate"
        slug = slugify(rec.get("title") or rec.get("record_id") or "untitled", max_len=50)
        suffix = (rec.get("pmid") or rec.get("doi") or rec.get("record_id") or "")[:12]
        suffix = slugify(suffix, max_len=16) or "x"
        fname = f"{year}-{slug}-{suffix}.md"
        if fname in used_names:
            fname = f"{year}-{slug}-{rec.get('record_id', 'x')[:8]}.md"
        used_names.add(fname)
        path = evidence_dir / fname
        content = _frontmatter(rec) + "\n" + _note_body(rec)
        path.write_text(content, encoding="utf-8")
        rel = f"10_Evidence/{fname}"
        rec["obsidian_path"] = rel
        count += 1

        if (
            rec.get("citation_status") == "approved"
            and rec.get("maps_to_market") == "KR_liquor_context"
        ):
            safe_path = safe_dir / fname
            safe_path.write_text(
                _frontmatter(rec)
                + "\n"
                + f"# Marketing-safe: {rec.get('title')}\n\n"
                + f"Source: [[{rel.replace('.md','')}]]\n\n"
                + f"**Allowed tone:** {rec.get('claim_text_allowed') or 'Objective ingredient / research-existence language only.'}\n",
                encoding="utf-8",
            )

    write_jsonl(EVIDENCE_JSONL, records)
    print(f"[obsidian] wrote {count} notes -> {evidence_dir}")
    return count


def write_regulatory_seeds() -> None:
    """Seed regulatory notes into vault/20_Regulatory."""
    vault = vault_path()
    reg = vault / "20_Regulatory"
    reg.mkdir(parents=True, exist_ok=True)

    notes = {
        "FDA-Cordyceps-Overview.md": """---
tags: [regulatory, FDA]
jurisdiction: US
---

# FDA — Cordyceps / Cordycepin overview (marketing reference)

## Key facts
- Cordycepin is **not** an FDA-approved drug indication for consumer disease treatment claims.
- Cordyceps products sold as dietary supplements fall under **DSHEA**; only **structure/function** claims are generally contemplated, with mandatory disclaimer language where applicable.
- Using disease claims (treat/cure/prevent cancer, diabetes, etc.) can cause a product to be treated as an **unapproved new drug**.
- Warning letters historically cite Cordyceps marketers for **disease claims**, not merely for selling Cordyceps.

## Do not say
- "FDA approved cordycepin"
- "FDA confirmed efficacy"

## Safer framing (non-product-specific)
- "Cordycepin has been studied in the scientific literature; it is not an FDA-approved drug for treating disease."
""",
        "MFDS-KR-HFF-and-Liquor.md": """---
tags: [regulatory, MFDS, Korea]
jurisdiction: KR
---

# 식약처 / 한국 — 동충하초 HFF vs 주류 광고

## 건강기능식품
- *Cordyceps militaris* 등 고시 원료의 기능성 문구(예: 면역 기능)는 **HFF 제품**에 한정됩니다.
- 제왕충초 **담금주**가 HFF가 아니면 고시 클레임을 라벨·광고에 전용하지 마세요.

## 주류
- 음주가 체력·운동능력·질병 치료·정신건강에 도움이 된다는 식의 표현은 금지됩니다.
- 논문 인용 ≠ 광고 가능.

## 파이프라인 태그
- `KR_HFF_ref_only` — 내부 참조
- `KR_liquor_context` — 법무 승인 후 객관 소개만
- `research_only` — 소비자 광고 금지
""",
        "COMPLIANCE.md": """---
tags: [regulatory]
---

# Compliance shortcut

Repo canonical guide: `docs/COMPLIANCE.md` in the report_q-sarang repository.
""",
    }
    for name, body in notes.items():
        (reg / name).write_text(body, encoding="utf-8")


if __name__ == "__main__":
    write_regulatory_seeds()
    sync_obsidian()
