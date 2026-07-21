"""Shared paths, env, and I/O helpers."""

from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Iterable

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
NORM_DIR = DATA_DIR / "normalized"
EXPORT_DIR = DATA_DIR / "exports"
DEFAULT_VAULT = ROOT / "vault"

EVIDENCE_JSONL = NORM_DIR / "evidence.jsonl"
CLAIMS_MAP_CSV = DATA_DIR / "claims_map.csv"


def load_env() -> None:
    load_dotenv(ROOT / ".env")


def repo_path(*parts: str) -> Path:
    return ROOT.joinpath(*parts)


def ensure_dirs() -> None:
    for p in (RAW_DIR, NORM_DIR, EXPORT_DIR, DEFAULT_VAULT):
        p.mkdir(parents=True, exist_ok=True)
    for sub in (
        "00_Inbox",
        "10_Evidence",
        "20_Regulatory",
        "30_Marketing_Safe",
        "40_Blog",
        "90_Templates",
    ):
        (DEFAULT_VAULT / sub).mkdir(parents=True, exist_ok=True)


def load_yaml(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def vault_path() -> Path:
    load_env()
    override = os.getenv("OBSIDIAN_VAULT_PATH", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_VAULT


def new_record_id() -> str:
    return str(uuid.uuid4())


def slugify(text: str, max_len: int = 60) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return (s or "untitled")[:max_len]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    return n


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def empty_evidence_record(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "record_id": new_record_id(),
        "title": "",
        "authors": [],
        "year": None,
        "journal": "",
        "doi": "",
        "pmid": "",
        "pmcid": "",
        "openalex_id": "",
        "abstract": "",
        "url": "",
        "source_apis": [],
        "track": "",
        "compound": "unclear",
        "species": "unclear",
        "product_form": "unclear",
        "standardization": "",
        "study_type": "unclear",
        "study_phase": "n/a",
        "sample_size": None,
        "population": "",
        "intervention_dose": "",
        "intervention_duration": "",
        "comparator": "",
        "primary_outcomes": [],
        "adverse_events_reported": None,
        "evidence_strength": "F",
        "bias_risk": "unclear",
        "relevance_to_product": "unclear",
        "relevance_notes": "",
        "claim_category": "other",
        "claim_text_allowed": "",
        "claim_text_prohibited": "",
        "maps_to_market": "research_only",
        "jurisdiction_caveats": [],
        "regulatory_status_note": "",
        "risk_flags": [],
        "citation_status": "candidate",
        "reviewed_by": "",
        "review_date": "",
        "full_text_available": False,
        "oa_license": "unknown",
        "notion_page_id": "",
        "obsidian_path": "",
        "priority_review": False,
    }
    base.update(overrides)
    return base
