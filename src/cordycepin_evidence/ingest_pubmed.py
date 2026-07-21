"""PubMed E-utilities ingest."""

from __future__ import annotations

import os
import time
import xml.etree.ElementTree as ET
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .utils import RAW_DIR, load_env, load_yaml, write_json

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _api_key() -> str | None:
    load_env()
    key = os.getenv("NCBI_API_KEY", "").strip()
    return key or None


def _rate_sleep() -> None:
    # 10/s with key, ~3/s without
    time.sleep(0.12 if _api_key() else 0.34)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _get(path: str, params: dict[str, Any]) -> requests.Response:
    key = _api_key()
    if key:
        params = {**params, "api_key": key}
    r = requests.get(f"{BASE}/{path}", params=params, timeout=60)
    r.raise_for_status()
    return r


def search_pmids(term: str, retmax: int) -> list[str]:
    r = _get(
        "esearch.fcgi",
        {
            "db": "pubmed",
            "term": term,
            "retmax": retmax,
            "retmode": "json",
            "sort": "relevance",
        },
    )
    _rate_sleep()
    data = r.json()
    return data.get("esearchresult", {}).get("idlist", [])


def _text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return "".join(el.itertext()).strip()


def parse_pubmed_xml(xml_text: str) -> list[dict[str, Any]]:
    root = ET.fromstring(xml_text)
    articles: list[dict[str, Any]] = []
    for art in root.findall(".//PubmedArticle"):
        medline = art.find("MedlineCitation")
        article = medline.find("Article") if medline is not None else None
        pmid = _text(medline.find("PMID")) if medline is not None else ""
        title = _text(article.find("ArticleTitle")) if article is not None else ""

        abstract_parts = []
        if article is not None:
            for abs_el in article.findall(".//AbstractText"):
                label = abs_el.attrib.get("Label")
                t = _text(abs_el)
                abstract_parts.append(f"{label}: {t}" if label else t)
        abstract = "\n".join(abstract_parts)

        authors: list[str] = []
        if article is not None:
            for au in article.findall(".//Author"):
                last = _text(au.find("LastName"))
                fore = _text(au.find("ForeName"))
                if last or fore:
                    authors.append(f"{fore} {last}".strip())

        journal = ""
        year = None
        if article is not None:
            journal = _text(article.find(".//Journal/Title"))
            y = _text(article.find(".//JournalIssue/PubDate/Year"))
            if not y:
                medline_date = _text(article.find(".//JournalIssue/PubDate/MedlineDate"))
                y = medline_date[:4] if medline_date else ""
            if y.isdigit():
                year = int(y)

        doi = ""
        pmcid = ""
        for id_el in art.findall(".//ArticleId"):
            id_type = id_el.attrib.get("IdType", "")
            val = _text(id_el)
            if id_type == "doi":
                doi = val.lower()
            elif id_type == "pmc":
                pmcid = val

        articles.append(
            {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "journal": journal,
                "year": year,
                "doi": doi,
                "pmcid": pmcid,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
                "source_api": "pubmed",
            }
        )
    return articles


def fetch_details(pmids: list[str], batch_size: int = 50) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i in range(0, len(pmids), batch_size):
        batch = pmids[i : i + batch_size]
        r = _get(
            "efetch.fcgi",
            {"db": "pubmed", "id": ",".join(batch), "retmode": "xml"},
        )
        _rate_sleep()
        out.extend(parse_pubmed_xml(r.text))
    return out


def ingest_pubmed() -> list[dict[str, Any]]:
    cfg = load_yaml("search_queries.yaml")
    limits = cfg.get("limits", {})
    retmax = int(limits.get("per_track_pubmed", 150))
    min_year = int(cfg.get("filters", {}).get("min_year", 1990))

    all_rows: list[dict[str, Any]] = []
    for track_name, track in (cfg.get("tracks") or {}).items():
        term = track["pubmed"]
        print(f"[pubmed] track={track_name} searching...")
        pmids = search_pmids(term, retmax)
        print(f"[pubmed] track={track_name} pmids={len(pmids)}")
        rows = fetch_details(pmids)
        for row in rows:
            row["track"] = track_name
            row["relevance_default"] = track.get("relevance_default", "unclear")
            if row.get("year") and row["year"] < min_year:
                continue
            all_rows.append(row)

    out_path = RAW_DIR / "pubmed.json"
    write_json(out_path, all_rows)
    print(f"[pubmed] wrote {len(all_rows)} -> {out_path}")
    return all_rows


if __name__ == "__main__":
    ingest_pubmed()
