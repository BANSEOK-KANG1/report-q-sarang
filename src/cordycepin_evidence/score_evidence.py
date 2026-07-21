"""Score study type, species, compound, evidence strength; flag claim risks."""

from __future__ import annotations

import csv
import re
from typing import Any

from .utils import (
    CLAIMS_MAP_CSV,
    EVIDENCE_JSONL,
    EXPORT_DIR,
    load_yaml,
    read_jsonl,
    write_jsonl,
)


def _blob(rec: dict[str, Any]) -> str:
    parts = [
        rec.get("title") or "",
        rec.get("abstract") or "",
        " ".join(rec.get("authors") or []),
        rec.get("journal") or "",
    ]
    return " ".join(parts).lower()


def _match_any(text: str, patterns: list[str]) -> bool:
    for p in patterns:
        if p.lower() in text:
            return True
    return False


def detect_study_type(text: str, rules: dict[str, Any], title: str = "") -> str:
    patterns = rules.get("study_type_patterns") or {}
    title_l = (title or "").lower()
    if "systematic review" in title_l:
        return "systematic_review"
    if "meta-analysis" in title_l or "meta analysis" in title_l:
        return "meta_analysis"
    if re.search(r"\breview\b", title_l) and "clinical trial" not in title_l:
        return "review_narrative"

    # order matters: more specific first
    order = [
        "meta_analysis",
        "systematic_review",
        "rct",
        "case_report",
        "observational_human",
        "animal",
        "in_vitro",
        "review_narrative",
    ]
    for key in order:
        if _match_any(text, patterns.get(key) or []):
            # Avoid labeling narrative reviews as RCTs when they merely mention trials
            if key == "rct" and (
                "review" in title_l
                or "systematic review" in text[:500]
                or "this review" in text[:800]
            ):
                continue
            return key
    return "unclear"


def detect_species(text: str, rules: dict[str, Any], track: str) -> str:
    patterns = rules.get("species_patterns") or {}
    hits = []
    for key in ("militaris", "sinensis", "cs4", "cordycepin"):
        if _match_any(text, patterns.get(key) or []):
            hits.append(key)
    if track == "comparator_sinensis":
        return "Cordyceps_sinensis" if "sinensis" in hits or "cs4" in hits else "unclear"
    if "militaris" in hits and "sinensis" not in hits:
        return "Cordyceps_militaris"
    if "sinensis" in hits and "militaris" not in hits:
        return "Cordyceps_sinensis"
    if "cs4" in hits:
        return "Paecilomyces_hepiali_Cs4"
    if "militaris" in hits and "sinensis" in hits:
        return "mixed"
    if track == "militaris":
        return "Cordyceps_militaris"
    if track == "compound" and "cordycepin" in hits:
        return "unclear"  # compound-focused; species may be unspecified
    return "unclear"


def detect_compound(text: str, track: str) -> str:
    if "cordycepin" in text or "3-deoxyadenosine" in text or "3'-deoxyadenosine" in text:
        return "cordycepin"
    if track == "compound":
        return "cordycepin"
    if "extract" in text:
        return "cordyceps_extract"
    return "unclear"


def detect_claim_category(text: str, rules: dict[str, Any]) -> str:
    cats = rules.get("claim_categories") or {}
    best = "other"
    best_hits = 0
    for name, meta in cats.items():
        if name == "other":
            continue
        kws = meta.get("keywords") or []
        hits = sum(1 for k in kws if k.lower() in text)
        if hits > best_hits:
            best_hits = hits
            best = name
    return best


def evidence_strength(study_type: str) -> str:
    return {
        "rct": "A_human_RCT",
        "observational_human": "B_limited_human",
        "systematic_review": "F_review_only",
        "meta_analysis": "F_review_only",
        "animal": "C_animal",
        "in_vitro": "D_in_vitro",
        "review_narrative": "F_review_only",
        "case_report": "B_limited_human",
        "unclear": "F_review_only",
    }.get(study_type, "F_review_only")


def flag_risks(rec: dict[str, Any], text: str, rules: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    disease = [t.lower() for t in (rules.get("disease_terms") or [])]
    disease += [t.lower() for t in (rules.get("disease_terms_ko") or [])]
    for term in disease:
        if term and term in text:
            flags.append("disease_language")
            break

    species = rec.get("species") or ""
    track = rec.get("track") or ""
    if track == "compound" and species in (
        "Cordyceps_sinensis",
        "Paecilomyces_hepiali_Cs4",
    ):
        flags.append("species_mismatch")
    if track == "militaris" and species in (
        "Cordyceps_sinensis",
        "Paecilomyces_hepiali_Cs4",
    ):
        flags.append("species_mismatch")
    if track != "comparator_sinensis" and species in (
        "Cordyceps_sinensis",
        "Paecilomyces_hepiali_Cs4",
        "mixed",
    ):
        if "species_mismatch" not in flags:
            flags.append("species_mismatch")

    if rec.get("study_type") in ("in_vitro", "animal"):
        flags.append("preclinical_only")

    if not (rec.get("abstract") or "").strip():
        flags.append("missing_abstract")

    return sorted(set(flags))


def maps_to_market(rec: dict[str, Any], rules: dict[str, Any]) -> str:
    # Preserve human-approved liquor mapping
    if rec.get("citation_status") == "approved" and rec.get("maps_to_market") == "KR_liquor_context":
        return "KR_liquor_context"
    if rec.get("citation_status") in ("approved", "needs_legal_review", "rejected"):
        # keep existing if already reviewed
        existing = rec.get("maps_to_market")
        if existing:
            return existing

    study = rec.get("study_type") or "unclear"
    default_map = (rules.get("maps_by_study_type") or {}).get(study, "research_only")
    if "disease_language" in (rec.get("risk_flags") or []):
        return "research_only"
    if rec.get("species") in (
        "Cordyceps_sinensis",
        "Paecilomyces_hepiali_Cs4",
        "mixed",
    ) and rec.get("track") != "comparator_sinensis":
        return "research_only"
    return default_map


def score_all() -> list[dict[str, Any]]:
    rules = load_yaml("claim_rules.yaml")
    records = read_jsonl(EVIDENCE_JSONL)
    claims_rows: list[dict[str, str]] = []

    for rec in records:
        text = _blob(rec)
        # Only auto-fill if not manually locked — study_type always refreshed from text
        # unless citation_status is approved (still refresh scientific fields)
        rec["study_type"] = detect_study_type(text, rules, title=rec.get("title") or "")
        rec["species"] = detect_species(text, rules, rec.get("track") or "")
        rec["compound"] = detect_compound(text, rec.get("track") or "")
        rec["claim_category"] = detect_claim_category(text, rules)
        rec["evidence_strength"] = evidence_strength(rec["study_type"])
        rec["risk_flags"] = flag_risks(rec, text, rules)

        if rec.get("track") == "comparator_sinensis":
            rec["relevance_to_product"] = "extrapolated"
            rec["relevance_notes"] = "Comparator species / Cs-4 — do not equate to C. militaris cordycepin product"
        elif rec.get("track") == "compound":
            if rec.get("species") == "Cordyceps_militaris":
                rec["relevance_to_product"] = "direct"
            elif rec.get("compound") == "cordycepin":
                rec["relevance_to_product"] = "partial"
                rec["relevance_notes"] = rec.get("relevance_notes") or "Cordycepin-focused; verify species/form vs product"
        elif rec.get("track") == "militaris":
            rec["relevance_to_product"] = "partial" if rec.get("compound") != "cordycepin" else "direct"

        # citation status escalation
        if rec.get("citation_status") == "candidate":
            if "disease_language" in rec["risk_flags"]:
                rec["citation_status"] = "needs_legal_review"
            rec["maps_to_market"] = maps_to_market(rec, rules)
        else:
            rec["maps_to_market"] = maps_to_market(rec, rules)

        # jurisdiction caveats
        caveats = ["KR_liquor_no_disease_claims", "not_HFF_product"]
        if "disease_language" in rec["risk_flags"]:
            caveats.append("disease_language_in_source")
        if rec.get("maps_to_market") == "research_only":
            caveats.append("research_only")
        rec["jurisdiction_caveats"] = caveats

        claims_rows.append(
            {
                "record_id": rec["record_id"],
                "title": rec.get("title") or "",
                "year": str(rec.get("year") or ""),
                "study_type": rec.get("study_type") or "",
                "evidence_strength": rec.get("evidence_strength") or "",
                "claim_category": rec.get("claim_category") or "",
                "risk_flags": "|".join(rec.get("risk_flags") or []),
                "maps_to_market": rec.get("maps_to_market") or "",
                "citation_status": rec.get("citation_status") or "",
                "doi": rec.get("doi") or "",
                "pmid": rec.get("pmid") or "",
            }
        )

    # Priority review: rank and mark top 50 for human triage
    def _priority_score(r: dict[str, Any]) -> tuple:
        study_rank = {
            "rct": 0,
            "observational_human": 1,
            "systematic_review": 2,
            "meta_analysis": 2,
            "review_narrative": 3,
            "animal": 4,
            "in_vitro": 5,
            "case_report": 4,
            "unclear": 6,
        }.get(r.get("study_type") or "unclear", 6)
        rel_rank = {"direct": 0, "partial": 1, "extrapolated": 3, "unclear": 2}.get(
            r.get("relevance_to_product") or "unclear", 2
        )
        has_abs = 0 if (r.get("abstract") or "").strip() else 1
        mismatch = 1 if "species_mismatch" in (r.get("risk_flags") or []) else 0
        disease = 1 if "disease_language" in (r.get("risk_flags") or []) else 0
        track_rank = {"compound": 0, "militaris": 1, "comparator_sinensis": 4}.get(
            r.get("track") or "", 3
        )
        # lower is better
        return (has_abs, mismatch, track_rank, study_rank, rel_rank, disease, -(r.get("year") or 0))

    ranked = sorted(records, key=_priority_score)
    priority_ids = {r["record_id"] for r in ranked[:50]}
    for rec in records:
        rec["priority_review"] = rec["record_id"] in priority_ids

    write_jsonl(EVIDENCE_JSONL, records)

    CLAIMS_MAP_CSV.parent.mkdir(parents=True, exist_ok=True)
    with CLAIMS_MAP_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(claims_rows[0].keys()) if claims_rows else [])
        if claims_rows:
            writer.writeheader()
            writer.writerows(claims_rows)

    # priority export
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    priority = [r for r in records if r.get("priority_review")]
    priority = sorted(priority, key=_priority_score)
    pri_path = EXPORT_DIR / "priority_review.csv"
    fields = [
        "record_id",
        "title",
        "year",
        "study_type",
        "evidence_strength",
        "species",
        "compound",
        "claim_category",
        "risk_flags",
        "citation_status",
        "maps_to_market",
        "doi",
        "pmid",
        "url",
    ]
    with pri_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in priority:
            w.writerow(
                {
                    "record_id": r.get("record_id"),
                    "title": r.get("title"),
                    "year": r.get("year"),
                    "study_type": r.get("study_type"),
                    "evidence_strength": r.get("evidence_strength"),
                    "species": r.get("species"),
                    "compound": r.get("compound"),
                    "claim_category": r.get("claim_category"),
                    "risk_flags": "|".join(r.get("risk_flags") or []),
                    "citation_status": r.get("citation_status"),
                    "maps_to_market": r.get("maps_to_market"),
                    "doi": r.get("doi"),
                    "pmid": r.get("pmid"),
                    "url": r.get("url"),
                }
            )

    print(f"[score] scored {len(records)}; priority_review={len(priority)} -> {pri_path}")
    return records


if __name__ == "__main__":
    score_all()
