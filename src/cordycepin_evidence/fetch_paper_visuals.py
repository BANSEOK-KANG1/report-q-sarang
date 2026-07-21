"""Fetch paper visuals from Europe PMC, OpenAlex, Crossref APIs."""

from __future__ import annotations

import io
import json
import os
import re
import time
import zipfile
from pathlib import Path
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .utils import EXPORT_DIR, ROOT, load_env

EPMC_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"
OPENALEX_BASE = "https://api.openalex.org/works"
CROSSREF_BASE = "https://api.crossref.org/works"

FIGURES_DIR = ROOT / "web" / "public" / "research-figures"
VISUALS_JSON = EXPORT_DIR / "research_visuals.json"

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FIGURES = 4
REQUEST_DELAY = 0.35


def _session() -> requests.Session:
    load_env()
    s = requests.Session()
    s.headers["User-Agent"] = "cordycepin-evidence/0.1 (research pipeline)"
    email = os.getenv("OPENALEX_EMAIL", "").strip()
    if email:
        s.headers["mailto"] = email
    return s


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def _get_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any] | list[Any] | None:
    r = _session().get(url, params=params, timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def _epmc_core(pmid: str) -> dict[str, Any]:
    if not pmid:
        return {}
    data = _get_json(
        f"{EPMC_BASE}/search",
        {"query": f"EXT_ID:{pmid}", "format": "json", "resultType": "core", "pageSize": 1},
    )
    if not data or not isinstance(data, dict):
        return {}
    results = (data.get("resultList") or {}).get("result") or []
    if not results:
        return {}
    r = results[0]
    keywords: list[str] = []
    kw = r.get("keywordList")
    if isinstance(kw, dict):
        raw = kw.get("keyword")
        if isinstance(raw, list):
            keywords = [str(k) for k in raw]
        elif raw:
            keywords = [str(raw)]
    mesh: list[str] = []
    mh = r.get("meshHeadingList")
    if isinstance(mh, dict):
        for item in mh.get("meshHeading") or []:
            desc = (item or {}).get("descriptorName")
            if desc:
                mesh.append(str(desc))
    return {
        "pmcid": r.get("pmcid") or "",
        "journal": r.get("journalTitle") or "",
        "cited_by_count": r.get("citedByCount"),
        "keywords": keywords,
        "mesh_terms": mesh,
        "has_full_text": bool(r.get("fullTextIdList")),
        "is_open_access": r.get("isOpenAccess") == "Y",
    }


def _openalex(doi: str) -> dict[str, Any]:
    if not doi:
        return {}
    data = _get_json(f"{OPENALEX_BASE}/https://doi.org/{doi}")
    if not data or not isinstance(data, dict):
        return {}
    concepts = []
    for c in (data.get("concepts") or [])[:8]:
        if (c.get("score") or 0) >= 0.3:
            concepts.append(
                {
                    "name": c.get("display_name") or "",
                    "score": round(float(c.get("score") or 0), 3),
                    "level": c.get("level"),
                }
            )
    oa = data.get("open_access") or {}
    primary = data.get("primary_location") or {}
    return {
        "openalex_id": data.get("id") or "",
        "cited_by_count": data.get("cited_by_count"),
        "concepts": concepts,
        "oa_status": oa.get("oa_status") or "",
        "oa_url": oa.get("oa_url") or "",
        "landing_page": primary.get("landing_page_url") or "",
        "publication_year": data.get("publication_year"),
    }


def _crossref(doi: str) -> dict[str, Any]:
    if not doi:
        return {}
    data = _get_json(f"{CROSSREF_BASE}/{doi}")
    if not data or not isinstance(data, dict):
        return {}
    msg = data.get("message") or {}
    return {
        "reference_count": msg.get("reference-count"),
        "publisher": msg.get("publisher") or "",
        "license": ((msg.get("license") or [{}])[0] or {}).get("URL") or "",
    }


def _download_epmc_figures(pmcid: str, slug: str) -> list[dict[str, Any]]:
    if not pmcid:
        return []
    pmcid = pmcid.replace("PMC", "")
    pmcid_full = f"PMC{pmcid}" if not pmcid.startswith("PMC") else pmcid
    url = f"{EPMC_BASE}/{pmcid_full}/supplementaryFiles"
    try:
        r = _session().get(url, timeout=60)
        if r.status_code != 200 or r.content[:2] != b"PK":
            return []
    except requests.RequestException:
        return []

    out_dir = FIGURES_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    figures: list[dict[str, Any]] = []

    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        names = [
            n
            for n in zf.namelist()
            if Path(n).suffix.lower() in IMAGE_EXT and not n.startswith("__")
        ]
        for i, name in enumerate(names[:MAX_FIGURES]):
            safe = re.sub(r"[^a-zA-Z0-9._-]", "-", Path(name).name)
            dest = out_dir / safe
            dest.write_bytes(zf.read(name))
            figures.append(
                {
                    "type": "figure",
                    "src": f"/research-figures/{slug}/{safe}",
                    "caption": f"원문 Figure ({Path(name).stem}) — Europe PMC OA",
                    "source": "europepmc",
                    "filename": safe,
                }
            )
    return figures


def fetch_visuals_for_record(record: dict[str, Any], slug: str) -> dict[str, Any]:
    """Build visual manifest for one evidence record."""
    pmid = str(record.get("pmid") or "").strip()
    doi = str(record.get("doi") or "").strip()

    epmc: dict[str, Any] = {}
    openalex: dict[str, Any] = {}
    crossref: dict[str, Any] = {}
    figures: list[dict[str, Any]] = []

    try:
        if pmid:
            epmc = _epmc_core(pmid)
            time.sleep(REQUEST_DELAY)
    except Exception as exc:
        epmc = {"error": str(exc)}

    try:
        if doi:
            openalex = _openalex(doi)
            time.sleep(REQUEST_DELAY)
    except Exception as exc:
        openalex = {"error": str(exc)}

    try:
        if doi:
            crossref = _crossref(doi)
            time.sleep(REQUEST_DELAY)
    except Exception as exc:
        crossref = {"error": str(exc)}

    pmcid = epmc.get("pmcid") or record.get("pmcid") or ""
    if pmcid and epmc.get("is_open_access"):
        try:
            figures = _download_epmc_figures(str(pmcid), slug)
            time.sleep(REQUEST_DELAY)
        except Exception:
            figures = []

    cited = openalex.get("cited_by_count")
    if cited is None:
        cited = epmc.get("cited_by_count")

    return {
        "slug": slug,
        "record_id": record.get("record_id"),
        "doi": doi,
        "pmid": pmid,
        "pmcid": pmcid,
        "figures": figures,
        "keywords": epmc.get("keywords") or [],
        "mesh_terms": epmc.get("mesh_terms") or [],
        "concepts": openalex.get("concepts") or [],
        "cited_by_count": cited,
        "reference_count": crossref.get("reference_count"),
        "publisher": crossref.get("publisher") or "",
        "journal": epmc.get("journal") or record.get("journal") or "",
        "oa_status": openalex.get("oa_status") or "",
        "oa_url": openalex.get("oa_url") or record.get("url") or "",
        "apis": {
            "europepmc": bool(epmc),
            "openalex": bool(openalex) and "error" not in openalex,
            "crossref": bool(crossref) and "error" not in crossref,
        },
        "fetched_at": time.strftime("%Y-%m-%d"),
    }


def enrich_research_visuals(
    records_with_slugs: list[tuple[dict[str, Any], str]],
) -> dict[str, dict[str, Any]]:
    """Fetch visuals for all research pages; write master JSON."""
    manifests: dict[str, dict[str, Any]] = {}
    for i, (record, slug) in enumerate(records_with_slugs):
        print(f"[visuals] ({i + 1}/{len(records_with_slugs)}) {slug}")
        manifests[slug] = fetch_visuals_for_record(record, slug)

    VISUALS_JSON.parent.mkdir(parents=True, exist_ok=True)
    VISUALS_JSON.write_text(
        json.dumps(manifests, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    fig_count = sum(len(m.get("figures") or []) for m in manifests.values())
    print(f"[visuals] {len(manifests)} papers, {fig_count} figures -> {VISUALS_JSON}")
    return manifests
