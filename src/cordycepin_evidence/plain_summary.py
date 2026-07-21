"""할머니도 읽을 수 있는 쉬운 정리 (plain Korean, not literal translation)."""

from __future__ import annotations

import re
from typing import Any

from .multiview_translate import (
    GLOSSARY,
    SECTION_LABELS,
    _clean,
    _google_translate,
    _parse_abstract_sections,
    _split_sentences,
)

STUDY_GRANDMA: dict[str, str] = {
    "rct": "사람을 대상으로 한 비교 실험 논문",
    "observational_human": "사람들의 데이터를 모아 본 논문",
    "systematic_review": "여러 논문을 모아 정리한 글",
    "meta_analysis": "여러 연구 숫자를 합쳐 본 글",
    "animal": "아직 실험실·동물 단계 논문",
    "in_vitro": "시험관·접시 안에서 한 실험 논문",
    "review_narrative": "여러 연구를 읽고 정리한 글",
    "case_report": "한두 사례를 소개한 글",
    "unclear": "학술 논문",
}

TOPIC_HINTS: list[tuple[str, str]] = [
    ("immunomodul", "몸의 방어 반응(면역)과 관련된 연구 주제"),
    ("immune", "몸의 방어 반응(면역)과 관련된 연구 주제"),
    ("fatigue", "피곤함·기운과 관련된 연구 주제"),
    ("exercise", "운동·체력과 관련된 연구 주제"),
    ("endurance", "지구력·운동 지속과 관련된 연구 주제"),
    ("antioxidant", "산화 스트레스·항산화와 관련된 연구 주제"),
    ("anti-inflammatory", "염증 반응과 관련된 연구 주제"),
    ("inflammation", "염증 반응과 관련된 연구 주제"),
    ("bioavailability", "성분이 몸에서 얼마나 쓰이는지(흡수) 연구"),
    ("metabolic", "몸속 대사·에너지와 관련된 연구 주제"),
    ("cognitive", "기억·집중 등 뇌 활동과 관련된 연구 주제"),
    ("biological effect", "성분·버섯이 몸에서 어떤 반응을 보이는지"),
    ("bioactive", "몸에 작용할 수 있는 성분(생리활성) 연구"),
    ("biosynthesis", "코디세핀이 균류 안에서 어떻게 만들어지는지"),
    ("production", "코디세핀을 더 많이·안정적으로 만드는 방법"),
    ("fermentation", "버섯·균을 키우며 성분을 만드는 방법"),
    ("cultivation", "동충하초를 어떻게 키우면 좋은지"),
    ("culture condition", "재배 환경(온도·영양 등)이 성분에 미치는 영향"),
    ("review", "지금까지 나온 연구들을 한데 모아 정리"),
]

# 학술 표현 → 쉬운 말
SIMPLE_REPLACEMENTS: list[tuple[str, str]] = [
    (r"전임상", "아직 실험실·동물 단계"),
    (r"in vitro", "접시·시험관 안에서"),
    (r"in vivo", "살아 있는 동물 안에서"),
    (r"무작위 대조 시험", "두 그룹을 나눠 공정하게 비교한 실험"),
    (r"대사산물", "균이 만들어내는 물질"),
    (r"생합성", "자연스럽게 만들어지는 과정"),
    (r"발효", "균·버섯을 키우며 성분을 만드는 과정"),
    (r"고체 발효", "곡물·밥 같은 재료 위에서 키우는 방식"),
    (r"액체 발효", "물·액체 속에서 키우는 방식"),
    (r"자실체", "우리가 흔히 보는 버섯 몸통·과실체"),
    (r"균사", "눈에 잘 안 보이는 버섯 실"),
    (r"추출물", "물이나 술 등으로 뽑아낸 성분"),
    (r"시험관\(in vitro\)", "접시·시험관 안"),
    (r"체계적 문헌고찰", "논문 여러 편을 골라 정리한 글"),
    (r"서술적 리뷰", "논문들을 읽고 풀어 쓴 정리 글"),
    (r"상관관계", "함께 변하는지 여부"),
    (r"유의미한", "우연이 아닐 가능성이 있는"),
    (r"함량", "들어 있는 양"),
    (r"최적화", "조건을 맞춰 가장 좋게 만드는 것"),
    (r"바이오", "생물"),
    (r"미생물", "눈에 안 보이는 균·미생물"),
    (r"치료", "병을 고치"),
    (r"효능", "몸에 좋은 효과"),
    (r"Therapeutic", "연구 맥락의"),
    (r"therapeutic", "연구 맥락의"),
    (r"medicinal fungus", "연구용 버섯(동충하초)"),
    (r"Medicinal fungus", "연구용 버섯(동충하초)"),
]

GRANDMA_NEUTRALIZE: list[tuple[str, str]] = [
    ("다양한 병을 고치", "여러 연구 주제"),
    ("병을 고치", "연구에서 다루"),
    ("약용 곰팡이", "연구용 버섯(동충하초)"),
    ("약용 버섯", "연구용 버섯"),
    ("치료 특성", "연구 대상"),
    ("치료 목적", "연구 목적"),
    ("효능", "성분 특성"),
    ("면역력을 높", "면역 관련 연구"),
    ("항암", "연구용"),
    ("anticancer", "연구용"),
]


def _neutralize_for_grandma(text: str) -> str:
    out = text
    for old, new in GRANDMA_NEUTRALIZE:
        out = out.replace(old, new)
    return _simplify_korean(out)


def _topic_from_text(text: str) -> str:
    lower = text.lower()
    for key, phrase in TOPIC_HINTS:
        if key in lower:
            return phrase
    return "동충하초(버섯)와 코디세핀(성분 이름)에 관한 이야기"


def _simplify_korean(text: str) -> str:
    if not text:
        return ""
    out = text
    for pattern, repl in SIMPLE_REPLACEMENTS:
        out = re.sub(pattern, repl, out, flags=re.I)
    out = re.sub(r"\s+", " ", out).strip()
    return out


def _shorten(text: str, max_sentences: int = 3, max_chars: int = 320) -> str:
    simplified = _simplify_korean(text)
    if not simplified:
        return ""
    sents = _split_sentences(simplified)
    if not sents:
        sents = [simplified]
    picked: list[str] = []
    total = 0
    for s in sents:
        if len(picked) >= max_sentences:
            break
        if len(s) > max_chars:
            chunk = s[: max_chars - 1].rstrip() + "…"
            if total + len(chunk) <= max_chars or not picked:
                picked.append(chunk)
            break
        if total + len(s) > max_chars and picked:
            break
        picked.append(s)
        total += len(s)
    if not picked:
        picked.append(simplified[: max_chars - 1].rstrip() + "…")
    return " ".join(picked)


def _headline(record: dict[str, Any], title_ko: str) -> str:
    year = record.get("year") or ""
    topic = _topic_from_text(_clean(record.get("title") or "") + " " + title_ko)
    study = STUDY_GRANDMA.get(record.get("study_type") or "", "학술 논문")
    year_bit = f"{year}년에 나온 " if year else ""
    return f"{year_bit}{study}입니다. 핵심 주제는 「{topic}」입니다."


def _good_to_know(record: dict[str, Any]) -> list[str]:
    lines = [
        "이 글은 **술·담금주가 몸에 좋다**는 이야기가 아닙니다.",
        "연구실·논문에서 말하는 **생리활성·기능성 주제**를 할머니·할아버지도 읽기 쉽게 풀어 쓴 것입니다.",
        "**제품 효능·효과를 보장하거나 광고하지 않습니다.**",
    ]
    flags = record.get("risk_flags") or []
    st = record.get("study_type") or ""
    if "preclinical_only" in flags or st in ("animal", "in_vitro"):
        lines.append("아직 **사람에게 직접 먹여 본 실험**이 아닐 수 있습니다. 실험실·동물 단계 이야기입니다.")
    if "disease_language" in flags:
        lines.append("원문에는 **병·치료** 관련 표현이 있을 수 있으나, 여기서는 **연구 주제**만 쉽게 옮겼습니다.")
    if st == "rct":
        lines.append("사람을 대상으로 한 비교 실험이지만, **시료·용량이 제왕충초 담금주와 같지 않을 수 있습니다.**")
    lines.append("궁금하시면 아래 **원문·번역 참고**를 펼쳐 보시면 됩니다.")
    return lines


def _section_plain(label: str, en: str, ko_cached: str = "") -> str:
    if not en and not ko_cached:
        return ""
    ko = _shorten(ko_cached or _google_translate(en), max_sentences=4, max_chars=400)
    if not ko:
        return ""
    return f"**{label}** — {ko}"


def build_easy_read(
    record: dict[str, Any],
    abstract: str,
    title_ko: str = "",
    section_translations: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """
    Grandma-friendly structured summary.
    section_translations: optional pre-built sections with ko_literal to avoid re-translate.
    """
    sections_raw = _parse_abstract_sections(abstract)
    by_id = {s["id"]: s for s in (section_translations or []) if s.get("id")}

    def ko_for(key: str) -> str:
        if key in by_id:
            return by_id[key].get("ko_literal") or ""
        en = sections_raw.get(key) or ""
        return _google_translate(en) if en else ""

    what_bits: list[str] = []
    summary_ko = _shorten(ko_for("summary"), max_sentences=3, max_chars=400)
    for key in ("background", "objective", "purpose", "summary"):
        if key in sections_raw or key in by_id:
            bit = _shorten(ko_for(key), max_sentences=2, max_chars=220)
            if bit:
                what_bits.append(bit)
                if key != "summary":
                    break
    if not what_bits and summary_ko:
        what_bits.append(_shorten(summary_ko, max_sentences=2, max_chars=220))

    topic = _topic_from_text(_clean(record.get("title") or "") + " " + title_ko)
    what_is = (
        f"이 글은 「{topic}」에 대한 학술 정리입니다. "
        + _neutralize_for_grandma(_shorten(summary_ko or " ".join(what_bits), max_sentences=2, max_chars=240))
        if (summary_ko or what_bits)
        else f"이 글은 「{topic}」에 대한 학술 정리입니다."
    )

    did = ""
    for key in ("methods", "method"):
        if key in sections_raw or key in by_id:
            did = _shorten(ko_for(key), max_sentences=3, max_chars=350)
            break
    if not did and record.get("study_type") in ("review_narrative", "systematic_review", "meta_analysis"):
        did = "여러 편의 논문을 찾아 읽고, 공통점과 차이를 표로 정리했습니다."

    found = ""
    for key in ("results", "result", "conclusions", "conclusion"):
        if key in sections_raw or key in by_id:
            found = _shorten(ko_for(key), max_sentences=3, max_chars=350)
            break
    if not found and summary_ko:
        found = _shorten(summary_ko, max_sentences=4, max_chars=420)

    # 섹션별 쉬운 한 줄
    easy_sections: list[dict[str, str]] = []
    order = ("background", "methods", "results", "conclusions", "summary")
    labels_grandma = {
        "background": "왜 이 연구를 했나요?",
        "methods": "어떻게 했나요?",
        "results": "무엇이 나왔나요?",
        "conclusions": "저자들의 한마디",
        "summary": "한줄 요약",
    }
    seen: set[str] = set()
    for key in order:
        if key in seen:
            continue
        en = sections_raw.get(key) or (by_id.get(key) or {}).get("en") or ""
        if not en and key != "summary":
            continue
        if not en and key == "summary":
            en = _clean(abstract)
        if not en:
            continue
        seen.add(key)
        ko = ko_for(key) if key in by_id or key in sections_raw else _google_translate(en)
        plain = _shorten(ko, max_sentences=4, max_chars=320)
        if plain:
            easy_sections.append(
                {
                    "id": key,
                    "label": labels_grandma.get(key, SECTION_LABELS.get(key, key)),
                    "text": plain,
                }
            )

    return {
        "headline": _headline(record, title_ko),
        "what_is_this": _neutralize_for_grandma(what_is),
        "what_they_did": _neutralize_for_grandma(did) if did else "논문·데이터를 모아 분석·정리했습니다.",
        "what_they_found": _neutralize_for_grandma(found) if found else _neutralize_for_grandma(summary_ko[:280] + "…" if summary_ko else "아래 「조금 더 나눠 보면」을 참고해 주세요."),
        "good_to_know": _good_to_know(record),
        "sections": [
            {**s, "text": _neutralize_for_grandma(s["text"])} for s in easy_sections
        ],
    }
