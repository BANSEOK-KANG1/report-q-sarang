"""Europe PMC ingest for OA / full-text flags."""

from __future__ import annotations

import time
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .utils import RAW_DIR, load_yaml, write_json

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _search(query: str, page_size: int) -> dict[str, Any]:
    r = requests.get(
        BASE,
        params={
            "query": query,
            "format": "json",
            "pageSize": page_size,
            "resultType": "core",
        },
        timeout=60,
    )
    r.raise_for_status()
    time.sleep(0.2)
    return r.json()


def ingest_europepmc() -> list[dict[str, Any]]:
    cfg = load_yaml("search_queries.yaml")
    limits = cfg.get("limits", {})
    page_size = int(limits.get("per_track_europepmc", 80))
    min_year = int(cfg.get("filters", {}).get("min_year", 1990))

    all_rows: list[dict[str, Any]] = []
    for track_name, track in (cfg.get("tracks") or {}).items():
        q = track["europepmc"]
        print(f"[europepmc] track={track_name} searching...")
        data = _search(q, page_size)
        results = (data.get("resultList") or {}).get("result") or []
        for item in results:
            year = item.get("pubYear")
            year_i = int(year) if str(year).isdigit() else None
            if year_i and year_i < min_year:
                continue
            doi = (item.get("doi") or "").lower()
            pmid = str(item.get("pmid") or "")
            pmcid = str(item.get("pmcid") or "")
            is_oa = str(item.get("isOpenAccess", "")).lower() == "y"
            all_rows.append(
                {
                    "title": item.get("title") or "",
                    "abstract": item.get("abstractText") or "",
                    "authors": [
                        a.strip()
                        for a in (item.get("authorString") or "").split(",")
                        if a.strip()
                    ],
                    "journal": item.get("journalTitle") or "",
                    "year": year_i,
                    "doi": doi,
                    "pmid": pmid,
                    "pmcid": pmcid,
                    "url": (
                        f"https://europepmc.org/article/MED/{pmid}"
                        if pmid
                        else (f"https://doi.org/{doi}" if doi else "")
                    ),
                    "full_text_available": is_oa,
                    "oa_license": "oa" if is_oa else "unknown",
                    "source_api": "europepmc",
                    "track": track_name,
                    "relevance_default": track.get("relevance_default", "unclear"),
                }
            )
        print(f"[europepmc] track={track_name} rows={len(results)}")

    out_path = RAW_DIR / "europepmc.json"
    write_json(out_path, all_rows)
    print(f"[europepmc] wrote {len(all_rows)} -> {out_path}")
    return all_rows


if __name__ == "__main__":
    ingest_europepmc()
