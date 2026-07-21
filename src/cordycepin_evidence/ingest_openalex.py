"""OpenAlex works ingest for DOI enrichment and broader coverage."""

from __future__ import annotations

import os
import time
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .utils import RAW_DIR, load_env, load_yaml, write_json

BASE = "https://api.openalex.org"


def _mailto() -> str:
    load_env()
    return os.getenv("OPENALEX_EMAIL", "cordycepin-evidence@example.com").strip()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _get(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    params = dict(params or {})
    params["mailto"] = _mailto()
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    time.sleep(0.1)
    return r.json()


def _authors(work: dict[str, Any]) -> list[str]:
    out = []
    for a in work.get("authorships") or []:
        name = (a.get("author") or {}).get("display_name")
        if name:
            out.append(name)
    return out


def _doi(work: dict[str, Any]) -> str:
    doi = work.get("doi") or ""
    if doi.startswith("https://doi.org/"):
        doi = doi.replace("https://doi.org/", "")
    return doi.lower()


def search_track(query: str, per_page: int, min_year: int) -> list[dict[str, Any]]:
    # OpenAlex search endpoint
    url = f"{BASE}/works"
    params = {
        "search": query,
        "per_page": min(per_page, 100),
        "filter": f"from_publication_date:{min_year}-01-01",
        "sort": "relevance_score:desc",
    }
    data = _get(url, params)
    results = data.get("results") or []
    rows: list[dict[str, Any]] = []
    for w in results:
        abstract = ""
        inv = w.get("abstract_inverted_index")
        if isinstance(inv, dict) and inv:
            # reconstruct abstract
            positions: dict[int, str] = {}
            for word, idxs in inv.items():
                for i in idxs:
                    positions[i] = word
            abstract = " ".join(positions[i] for i in sorted(positions))

        pmid = ""
        for loc in w.get("ids") or {}:
            pass
        ids = w.get("ids") or {}
        pmid_url = ids.get("pmid") or ""
        if "pubmed.ncbi.nlm.nih.gov/" in pmid_url:
            pmid = pmid_url.rstrip("/").split("/")[-1]

        rows.append(
            {
                "openalex_id": (w.get("id") or "").replace("https://openalex.org/", ""),
                "title": w.get("display_name") or w.get("title") or "",
                "abstract": abstract,
                "authors": _authors(w),
                "journal": ((w.get("primary_location") or {}).get("source") or {}).get(
                    "display_name"
                )
                or "",
                "year": w.get("publication_year"),
                "doi": _doi(w),
                "pmid": pmid,
                "pmcid": "",
                "url": w.get("doi")
                or ids.get("pmid")
                or w.get("id")
                or "",
                "cited_by_count": w.get("cited_by_count"),
                "is_oa": (w.get("open_access") or {}).get("is_oa"),
                "oa_url": (w.get("open_access") or {}).get("oa_url"),
                "source_api": "openalex",
            }
        )
    return rows


def ingest_openalex() -> list[dict[str, Any]]:
    cfg = load_yaml("search_queries.yaml")
    limits = cfg.get("limits", {})
    per = int(limits.get("per_track_openalex", 100))
    min_year = int(cfg.get("filters", {}).get("min_year", 1990))

    all_rows: list[dict[str, Any]] = []
    for track_name, track in (cfg.get("tracks") or {}).items():
        q = track["openalex"]
        print(f"[openalex] track={track_name} searching...")
        rows = search_track(q, per, min_year)
        for row in rows:
            row["track"] = track_name
            row["relevance_default"] = track.get("relevance_default", "unclear")
            all_rows.append(row)
        print(f"[openalex] track={track_name} rows={len(rows)}")

    out_path = RAW_DIR / "openalex.json"
    write_json(out_path, all_rows)
    print(f"[openalex] wrote {len(all_rows)} -> {out_path}")
    return all_rows


if __name__ == "__main__":
    ingest_openalex()
