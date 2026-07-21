"""Multi-perspective Korean translation of paper abstracts."""

from __future__ import annotations

import re
import time
from typing import Any

# Domain glossary — EN term -> (KO, short note)
GLOSSARY: dict[str, tuple[str, str]] = {
    "cordycepin": ("코디세핀", "3'-deoxyadenosine, Cordyceps 주요 bioactive 성분"),
    "cordyceps militaris": ("Cordyceps militaris", "동충하초 균종"),
    "cordyceps": ("Cordyceps", "충Cordyceps属 진균"),
    "biosynthesis": ("생합성", "생물체 내에서 물질이 만들어지는 과정"),
    "fermentation": ("발효", "미생물·균류를 이용한 대량 배양"),
    "solid-state fermentation": ("고체 발효", "곡물·기질 위 고체 상태 배양"),
    "liquid fermentation": ("액체 발효", "액체 배지에서의 submerged 배양"),
    "metabolite": ("대사산물", "균류·세포가 만든 화학물질"),
    "in vitro": ("시험관(in vitro)", "생체 밖 실험"),
    "in vivo": ("생체(in vivo)", "동물 등 생체 내 실험"),
    "randomized": ("무작위 배정", "RCT 설계"),
    "double-blind": ("이중 맹검", "실험자·피험자 모두 처리 모름"),
    "systematic review": ("체계적 문헌고찰", "검색·선별·종합 절차가 정해진 리뷰"),
    "meta-analysis": ("메타분석", "여러 연구 결과를 통계적으로 통합"),
    "polysaccharide": ("다당류", "당이 연결된 고분자"),
    "adenosine": ("아데노신", "뉴클레오시드 관련 물질"),
    "ergosterol": ("에르고스테롤", "진균 세포막 스테롤"),
    "mycelium": ("균사", "균류의 실체 영양체"),
    "fruiting body": ("자실체", "균류의 번식·수확 대상 구조"),
    "cultivation": ("재배·배양", "인공 조건에서 균류 키우기"),
    "yield": ("수율", "단위당 생산량"),
    "extract": ("추출물", "용매 등으로 뽑아낸 성분"),
}

SECTION_LABELS: dict[str, str] = {
    "background": "연구 배경",
    "objective": "연구 목적",
    "purpose": "연구 목적",
    "methods": "연구 방법",
    "method": "연구 방법",
    "results": "주요 결과",
    "result": "주요 결과",
    "conclusions": "저자 결론",
    "conclusion": "저자 결론",
    "summary": "초록 전체",
}

PLAIN_INTROS: dict[str, str] = {
    "background": "이 연구는 다음 배경에서 출발합니다.",
    "methods": "연구팀은 대략 이렇게 실험·분석을 진행했습니다.",
    "results": "실험·분석에서 관찰된 핵심 내용은 다음과 같습니다.",
    "conclusions": "저자들은 결과를 이렇게 해석·정리했습니다.",
    "summary": "논문 초록의 요지를 쉽게 풀면 다음과 같습니다.",
}


def _clean(text: str) -> str:
    from html import unescape

    t = unescape(text or "")
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(<\"])", text)
    return [p.strip() for p in parts if p.strip()]


def _protect_terms(text: str) -> tuple[str, dict[str, str]]:
    """Replace glossary terms with placeholders before MT."""
    protected = text
    mapping: dict[str, str] = {}
    for i, (en, (ko, _)) in enumerate(
        sorted(GLOSSARY.items(), key=lambda x: -len(x[0]))
    ):
        pattern = re.compile(re.escape(en), re.I)

        def repl(m: re.Match, idx=i, term=ko) -> str:
            key = f"__TERM{idx}__"
            mapping[key] = term
            return key

        protected = pattern.sub(repl, protected)
    return protected, mapping


def _restore_terms(text: str, mapping: dict[str, str]) -> str:
    for key, ko in mapping.items():
        text = text.replace(key, ko)
    return text


def _google_translate(text: str, dest: str = "ko") -> str:
    if not text or not text.strip():
        return ""
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        return _glossary_substitute(text)

    protected, term_map = _protect_terms(text)
    chunk_size = 4500
    chunks: list[str] = []
    buf = protected
    while buf:
        if len(buf) <= chunk_size:
            chunks.append(buf)
            break
        cut = buf.rfind(". ", 0, chunk_size)
        if cut < 800:
            cut = chunk_size
        chunks.append(buf[: cut + 1].strip())
        buf = buf[cut + 1 :].strip()

    out: list[str] = []
    translator = GoogleTranslator(source="auto", target=dest)
    for i, chunk in enumerate(chunks):
        if i:
            time.sleep(0.25)
        try:
            translated = translator.translate(chunk)
            out.append(_restore_terms(translated, term_map))
        except Exception:
            out.append(_glossary_substitute(_restore_terms(chunk, term_map)))
    return " ".join(out).strip()


def _glossary_substitute(text: str) -> str:
    """Fallback: annotate known EN terms inline."""
    result = text
    for en, (ko, note) in sorted(GLOSSARY.items(), key=lambda x: -len(x[0])):
        pattern = re.compile(re.escape(en), re.I)
        if pattern.search(result):
            result = pattern.sub(f"{ko}({en})", result, count=1)
    return result


def _extract_glossary(text: str) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    lower = text.lower()
    for en, (ko, note) in GLOSSARY.items():
        if en in lower:
            found.append({"en": en, "ko": ko, "note": note})
    return found[:12]


def _researcher_view(en: str, ko_literal: str, section_key: str) -> str:
    st = SECTION_LABELS.get(section_key, section_key)
    glossary = _extract_glossary(en)
    terms = ""
    if glossary:
        terms = " · ".join(f"**{g['ko']}**({g['en']})" for g in glossary[:4])
    lead = f"[{st}] "
    if terms:
        lead += f"핵심 용어: {terms}. "
    body = ko_literal or _glossary_substitute(en)
    return lead + body


def _plain_view(en: str, ko_literal: str, section_key: str) -> str:
    intro = PLAIN_INTROS.get(section_key, "이 부분을 쉽게 정리하면 다음과 같습니다.")
    sentences = _split_sentences(ko_literal or en)
    if len(sentences) > 3:
        body = " ".join(sentences[:3]) + " …"
    else:
        body = ko_literal or en
    return f"{intro} {body}"


def _parse_abstract_sections(abstract: str) -> dict[str, str]:
    raw = abstract or ""
    sections: dict[str, str] = {}
    parts = re.split(
        r"<h4>\s*(Background|Methods|Results|Conclusions?|Objective|Purpose)\s*</h4>",
        raw,
        flags=re.I,
    )
    if len(parts) > 1:
        i = 1
        while i + 1 < len(parts):
            key = parts[i].strip().lower()
            body = _clean(parts[i + 1])
            if body:
                sections[key.rstrip("s")] = body
            i += 2
    if not sections:
        plain = _clean(raw)
        if plain:
            sections["summary"] = plain
    return sections


def build_multiview_translations(
    abstract: str,
    title: str = "",
) -> dict[str, Any]:
    """Build multi-angle translation payload for frontmatter."""
    sections_raw = _parse_abstract_sections(abstract)
    title_en = _clean(title)
    title_ko = _google_translate(title_en) if title_en else ""

    section_list: list[dict[str, str]] = []
    order = (
        "background",
        "objective",
        "purpose",
        "methods",
        "method",
        "results",
        "result",
        "conclusions",
        "conclusion",
        "summary",
    )
    seen: set[str] = set()
    keys = [k for k in order if k in sections_raw] + [
        k for k in sections_raw if k not in order
    ]

    for key in keys:
        if key in seen:
            continue
        seen.add(key)
        en = sections_raw[key]
        if not en:
            continue
        ko_literal = _google_translate(en)
        time.sleep(0.2)
        section_list.append(
            {
                "id": key,
                "label_ko": SECTION_LABELS.get(key, key),
                "en": en,
                "ko_literal": ko_literal,
                "ko_researcher": _researcher_view(en, ko_literal, key),
                "ko_plain": _plain_view(en, ko_literal, key),
            }
        )

    full_en = _clean(abstract)
    full_ko = _google_translate(full_en) if full_en else ""

    return {
        "title_ko": title_ko,
        "glossary": _extract_glossary(full_en or title_en),
        "sections": section_list,
        "full": {
            "en": full_en,
            "ko_literal": full_ko,
            "ko_researcher": _researcher_view(full_en, full_ko, "summary"),
            "ko_plain": _plain_view(full_en, full_ko, "summary"),
        },
    }
