"""Normalize and deduplicate raw API records into evidence.jsonl."""

from __future__ import annotations

import re
from typing import Any

from .utils import (
    EVIDENCE_JSONL,
    RAW_DIR,
    empty_evidence_record,
    read_json,
    read_jsonl,
    write_jsonl,
)


def _norm_title(title: str) -> str:
    t = title.lower().strip()
    t = re.sub(r"[^a-z0-9\s]", "", t)
    t = re.sub(r"\s+", " ", t)
    return t


def _dedup_key(row: dict[str, Any]) -> str:
    doi = (row.get("doi") or "").lower().strip()
    if doi:
        return f"doi:{doi}"
    pmid = str(row.get("pmid") or "").strip()
    if pmid:
        return f"pmid:{pmid}"
    title = _norm_title(row.get("title") or "")
    year = row.get("year") or ""
    return f"ty:{title}|{year}"


def _merge(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Prefer non-empty fields; union lists."""
    out = dict(a)
    for k, v in b.items():
        if k == "source_apis":
            out[k] = sorted(set((out.get(k) or []) + (v or [])))
            continue
        if k == "authors":
            if len(v or []) > len(out.get(k) or []):
                out[k] = v
            continue
        if k in ("abstract", "title", "journal", "doi", "pmid", "pmcid", "url", "openalex_id"):
            if (not out.get(k)) and v:
                out[k] = v
            elif k == "abstract" and v and len(str(v)) > len(str(out.get(k) or "")):
                out[k] = v
            continue
        if k == "full_text_available":
            out[k] = bool(out.get(k)) or bool(v)
            continue
        if k == "year" and not out.get(k) and v:
            out[k] = v
            continue
        if k == "track":
            # prefer compound > militaris > comparator for primary track label
            rank = {"compound": 0, "militaris": 1, "comparator_sinensis": 2}
            cur = out.get(k) or "zzz"
            if rank.get(v, 99) < rank.get(cur, 99):
                out[k] = v
            continue
        if k == "relevance_to_product":
            rank = {"direct": 0, "partial": 1, "extrapolated": 2, "unclear": 3, "na": 4}
            cur = out.get(k) or "unclear"
            if rank.get(v, 99) < rank.get(cur, 99):
                out[k] = v
            continue
    return out


def _raw_to_evidence(row: dict[str, Any]) -> dict[str, Any]:
    source = row.get("source_api") or "unknown"
    rec = empty_evidence_record(
        title=row.get("title") or "",
        authors=row.get("authors") or [],
        year=row.get("year"),
        journal=row.get("journal") or "",
        doi=(row.get("doi") or "").lower(),
        pmid=str(row.get("pmid") or ""),
        pmcid=str(row.get("pmcid") or ""),
        openalex_id=row.get("openalex_id") or "",
        abstract=row.get("abstract") or "",
        url=row.get("url") or "",
        source_apis=[source],
        track=row.get("track") or "",
        relevance_to_product=row.get("relevance_default") or "unclear",
        full_text_available=bool(row.get("full_text_available")),
        oa_license=row.get("oa_license") or ("oa" if row.get("is_oa") else "unknown"),
    )
    return rec


def load_raw_sources() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in ("pubmed.json", "openalex.json", "europepmc.json"):
        path = RAW_DIR / name
        if path.exists():
            rows.extend(read_json(path))
    return rows


def normalize(existing_preserve: bool = True) -> list[dict[str, Any]]:
    """Merge raw into normalized evidence. Preserve review fields on existing keys."""
    raw = load_raw_sources()
    merged: dict[str, dict[str, Any]] = {}

    prior_by_key: dict[str, dict[str, Any]] = {}
    if existing_preserve and EVIDENCE_JSONL.exists():
        for rec in read_jsonl(EVIDENCE_JSONL):
            prior_by_key[_dedup_key(rec)] = rec

    for row in raw:
        if not (row.get("title") or row.get("doi") or row.get("pmid")):
            continue
        ev = _raw_to_evidence(row)
        key = _dedup_key(ev)
        if key in merged:
            merged[key] = _merge(merged[key], ev)
        else:
            merged[key] = ev

    # restore human review fields
    preserve_fields = (
        "citation_status",
        "reviewed_by",
        "review_date",
        "claim_text_allowed",
        "claim_text_prohibited",
        "notion_page_id",
        "obsidian_path",
        "regulatory_status_note",
        "maps_to_market",
        "priority_review",
    )
    out: list[dict[str, Any]] = []
    for key, rec in merged.items():
        if key in prior_by_key:
            old = prior_by_key[key]
            rec["record_id"] = old.get("record_id") or rec["record_id"]
            for f in preserve_fields:
                if old.get(f) not in (None, "", [], "candidate") or f in (
                    "notion_page_id",
                    "obsidian_path",
                    "claim_text_allowed",
                    "claim_text_prohibited",
                    "reviewed_by",
                    "review_date",
                    "regulatory_status_note",
                ):
                    # Keep approved/rejected/needs_legal_review; also keep ids/paths
                    if f == "citation_status" and old.get(f) and old[f] != "candidate":
                        rec[f] = old[f]
                    elif f == "maps_to_market" and old.get(f) and old.get("citation_status") in (
                        "approved",
                        "needs_legal_review",
                        "rejected",
                    ):
                        rec[f] = old[f]
                    elif f != "citation_status" and f != "maps_to_market" and old.get(f):
                        rec[f] = old[f]
                    elif f == "priority_review":
                        rec[f] = old.get(f, False)
        out.append(rec)

    # Prefer rows with abstracts when sorting later
    out.sort(key=lambda r: (0 if r.get("abstract") else 1, -(r.get("year") or 0), r.get("title") or ""))
    n = write_jsonl(EVIDENCE_JSONL, out)
    print(f"[normalize] {n} records -> {EVIDENCE_JSONL}")
    return out


if __name__ == "__main__":
    normalize()
