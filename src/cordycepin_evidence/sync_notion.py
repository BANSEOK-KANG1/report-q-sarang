"""Sync evidence records to a Notion database (create DB if needed)."""

from __future__ import annotations

import os
from typing import Any

from .utils import EVIDENCE_JSONL, load_env, read_jsonl, write_jsonl

# Notion property schema
DB_PROPERTIES: dict[str, Any] = {
    "Name": {"title": {}},
    "Record ID": {"rich_text": {}},
    "Year": {"number": {}},
    "DOI": {"rich_text": {}},
    "PMID": {"rich_text": {}},
    "Study Type": {
        "select": {
            "options": [
                {"name": n}
                for n in [
                    "in_vitro",
                    "animal",
                    "rct",
                    "observational_human",
                    "systematic_review",
                    "meta_analysis",
                    "review_narrative",
                    "case_report",
                    "unclear",
                ]
            ]
        }
    },
    "Evidence Strength": {"select": {"options": [{"name": n} for n in [
        "A_human_RCT",
        "B_limited_human",
        "C_animal",
        "D_in_vitro",
        "E_traditional",
        "F_review_only",
    ]]}},
    "Species": {"rich_text": {}},
    "Compound": {"select": {"options": [
        {"name": "cordycepin"},
        {"name": "cordyceps_extract"},
        {"name": "unclear"},
        {"name": "other"},
    ]}},
    "Claim Category": {"select": {"options": [
        {"name": n}
        for n in [
            "immune",
            "energy_fatigue",
            "exercise_performance",
            "antioxidant",
            "metabolic",
            "respiratory",
            "cognitive",
            "anti_inflammatory",
            "other",
        ]
    ]}},
    "Maps To Market": {"select": {"options": [
        {"name": "research_only"},
        {"name": "KR_liquor_context"},
        {"name": "KR_HFF_ref_only"},
        {"name": "US_structure_function_ref"},
    ]}},
    "Citation Status": {"select": {"options": [
        {"name": "candidate"},
        {"name": "needs_legal_review"},
        {"name": "approved"},
        {"name": "rejected"},
    ]}},
    "Risk Flags": {"multi_select": {"options": [
        {"name": "disease_language"},
        {"name": "species_mismatch"},
        {"name": "preclinical_only"},
        {"name": "missing_abstract"},
        {"name": "dose_mismatch"},
    ]}},
    "Priority Review": {"checkbox": {}},
    "URL": {"url": {}},
    "Track": {"rich_text": {}},
    "Obsidian Path": {"rich_text": {}},
}


def _rt(text: str) -> list[dict[str, Any]]:
    text = (text or "")[:2000]
    return [{"type": "text", "text": {"content": text}}] if text else []


def _client():
    load_env()
    token = os.getenv("NOTION_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "NOTION_TOKEN missing. Set it in .env (see .env.example). Skipping Notion sync."
        )
    try:
        from notion_client import Client
    except ImportError as e:
        raise SystemExit("notion-client not installed. pip install -e .") from e
    return Client(auth=token)


def ensure_database() -> str:
    load_env()
    db_id = os.getenv("NOTION_DB_ID", "").strip()
    if db_id:
        return db_id
    parent = os.getenv("NOTION_PARENT_PAGE_ID", "").strip()
    if not parent:
        raise SystemExit(
            "Set NOTION_DB_ID or NOTION_PARENT_PAGE_ID in .env to sync Notion."
        )
    client = _client()
    db = client.databases.create(
        parent={"type": "page_id", "page_id": parent},
        title=[{"type": "text", "text": {"content": "Cordycepin Evidence (Q-Sarang)"}}],
        properties=DB_PROPERTIES,
    )
    new_id = db["id"]
    print(f"[notion] created database {new_id}")
    print("Add to .env: NOTION_DB_ID=" + new_id.replace("-", ""))
    return new_id


def _props_from_rec(rec: dict[str, Any]) -> dict[str, Any]:
    url = rec.get("url") or None
    if url and not str(url).startswith("http"):
        url = None
    risk = rec.get("risk_flags") or []
    return {
        "Name": {"title": [{"type": "text", "text": {"content": (rec.get("title") or "Untitled")[:2000]}}]},
        "Record ID": {"rich_text": _rt(rec.get("record_id") or "")},
        "Year": {"number": rec.get("year")},
        "DOI": {"rich_text": _rt(rec.get("doi") or "")},
        "PMID": {"rich_text": _rt(rec.get("pmid") or "")},
        "Study Type": {"select": {"name": rec.get("study_type") or "unclear"}},
        "Evidence Strength": {
            "select": {"name": rec.get("evidence_strength") or "F_review_only"}
        },
        "Species": {"rich_text": _rt(rec.get("species") or "")},
        "Compound": {"select": {"name": rec.get("compound") or "unclear"}},
        "Claim Category": {"select": {"name": rec.get("claim_category") or "other"}},
        "Maps To Market": {
            "select": {"name": rec.get("maps_to_market") or "research_only"}
        },
        "Citation Status": {
            "select": {"name": rec.get("citation_status") or "candidate"}
        },
        "Risk Flags": {"multi_select": [{"name": x} for x in risk]},
        "Priority Review": {"checkbox": bool(rec.get("priority_review"))},
        "URL": {"url": url},
        "Track": {"rich_text": _rt(rec.get("track") or "")},
        "Obsidian Path": {"rich_text": _rt(rec.get("obsidian_path") or "")},
    }


def _query_existing(client: Any, db_id: str) -> dict[str, str]:
    """Map external key (doi|pmid|record_id) -> page_id."""
    mapping: dict[str, str] = {}
    cursor = None
    while True:
        kwargs: dict[str, Any] = {"database_id": db_id, "page_size": 100}
        if cursor:
            kwargs["start_cursor"] = cursor
        resp = client.databases.query(**kwargs)
        for page in resp.get("results") or []:
            pid = page["id"]
            props = page.get("properties") or {}
            doi = ""
            pmid = ""
            rid = ""
            try:
                doi_rt = props.get("DOI", {}).get("rich_text") or []
                doi = (doi_rt[0]["plain_text"] if doi_rt else "").lower()
            except (KeyError, IndexError, TypeError):
                pass
            try:
                pmid_rt = props.get("PMID", {}).get("rich_text") or []
                pmid = pmid_rt[0]["plain_text"] if pmid_rt else ""
            except (KeyError, IndexError, TypeError):
                pass
            try:
                rid_rt = props.get("Record ID", {}).get("rich_text") or []
                rid = rid_rt[0]["plain_text"] if rid_rt else ""
            except (KeyError, IndexError, TypeError):
                pass
            if doi:
                mapping[f"doi:{doi}"] = pid
            if pmid:
                mapping[f"pmid:{pmid}"] = pid
            if rid:
                mapping[f"rid:{rid}"] = pid
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return mapping


def sync_notion(limit: int | None = None) -> int:
    load_env()
    if not os.getenv("NOTION_TOKEN", "").strip():
        print("[notion] NOTION_TOKEN not set — writing sync stub only.")
        stub = EVIDENCE_JSONL.parent / "notion_sync_pending.txt"
        stub.write_text(
            "Set NOTION_TOKEN and NOTION_DB_ID (or NOTION_PARENT_PAGE_ID) in .env, then run: cordycepin sync-notion\n",
            encoding="utf-8",
        )
        return 0

    client = _client()
    db_id = ensure_database()
    existing = _query_existing(client, db_id)
    records = read_jsonl(EVIDENCE_JSONL)
    if limit:
        records = records[:limit]

    updated = 0
    for rec in records:
        key = None
        if rec.get("doi"):
            key = f"doi:{rec['doi'].lower()}"
        elif rec.get("pmid"):
            key = f"pmid:{rec['pmid']}"
        else:
            key = f"rid:{rec['record_id']}"

        props = _props_from_rec(rec)
        page_id = existing.get(key) or rec.get("notion_page_id")
        try:
            if page_id:
                client.pages.update(page_id=page_id, properties=props)
            else:
                page = client.pages.create(
                    parent={"database_id": db_id}, properties=props
                )
                page_id = page["id"]
                existing[key] = page_id
            rec["notion_page_id"] = page_id
            updated += 1
        except Exception as e:  # noqa: BLE001
            print(f"[notion] failed for {rec.get('title', '')[:60]}: {e}")

    write_jsonl(EVIDENCE_JSONL, records)
    print(f"[notion] upserted {updated} pages")
    return updated


if __name__ == "__main__":
    sync_notion()
