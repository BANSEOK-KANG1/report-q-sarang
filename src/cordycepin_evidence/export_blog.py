"""Generate editorial blog posts for Q-Sarang (not citation dumps)."""

from __future__ import annotations

import csv
import re
from datetime import date
from html import unescape
from pathlib import Path
from typing import Any

import yaml

from .utils import EVIDENCE_JSONL, EXPORT_DIR, ROOT, load_yaml, read_jsonl, vault_path


def _clean(text: str) -> str:
    t = unescape(text or "")
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _pick_refs(records: list[dict[str, Any]], limit: int = 2) -> list[dict[str, Any]]:
    """Prefer biosynthesis / species context papers — not disease titles."""
    approved = [
        r
        for r in records
        if r.get("citation_status") == "approved"
        and r.get("maps_to_market") == "KR_liquor_context"
    ]
    pool = approved or [
        r
        for r in records
        if r.get("track") in ("compound", "militaris")
        and "disease_language" not in (r.get("risk_flags") or [])
        and (r.get("abstract") or "").strip()
        and r.get("relevance_to_product") in ("direct", "partial")
    ]
    # Prefer titles about biosynthesis / Cordyceps militaris production
    def score(r: dict[str, Any]) -> tuple:
        title = (_clean(r.get("title") or "")).lower()
        prefer = any(
            k in title
            for k in (
                "biosynthesis",
                "production",
                "militaris",
                "cultivation",
                "metabol",
                "adenosine",
            )
        )
        return (0 if prefer else 1, -(r.get("year") or 0))

    return sorted(pool, key=score)[:limit]


def _further_reading(recs: list[dict[str, Any]]) -> str:
    if not recs:
        return ""
    lines = [
        "## 참고하면 좋은 자료",
        "",
        "아래는 성분·균류를 **연구 주제**로 다루는 학술 문헌입니다. "
        "제품의 효능을 설명하거나 보장하는 근거가 아닙니다.",
        "",
    ]
    for r in recs:
        title = _clean(r.get("title") or "")
        year = r.get("year") or ""
        url = r.get("url") or (
            f"https://doi.org/{r['doi']}" if r.get("doi") else ""
        )
        if url:
            lines.append(f"- {year} · [{title}]({url})")
        else:
            lines.append(f"- {year} · {title}")
    lines.append("")
    return "\n".join(lines)


def _series_nav() -> str:
    return """
## 이 시리즈 이어서 읽기

1. 코디세핀, 이름이 낯설다면
2. 제왕충초가 가리키는 균류 — Cordyceps militaris
3. 코디세핀 논문이 보여도 제품 소개로 옮기지 않는 이유
4. FDA·식약처 이름을 붙이기 전에
5. 큐사랑 제왕충초 담금주
""".strip()


def _frontmatter(post: dict[str, Any], description: str) -> str:
    data = {
        "title": post["title"],
        "slug": post["slug"],
        "date": date.today().isoformat(),
        "brand": "큐사랑",
        "product": "제왕충초 담금주",
        "category": post.get("category"),
        "keywords": post.get("keywords") or [],
        "status": post.get("status", "draft"),
        "compliance": "KR_liquor_objective_only",
        "no_disease_claims": True,
        "no_efficacy_claims": True,
        "description": description,
        "tags": ["blog", "cordycepin", "제왕충초", "큐사랑"],
        "generated": date.today().isoformat(),
    }
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{body}\n---\n"


def _footer(cfg: dict[str, Any]) -> str:
    return (cfg.get("disclaimer") or "").strip()


# ---------------------------------------------------------------------------
# Editorial bodies
# ---------------------------------------------------------------------------


def render_what_is_cordycepin(cfg: dict[str, Any], refs: str) -> str:
    d = _footer(cfg)
    return f"""
동충하초 이야기를 듣다 보면, 어느 순간 **코디세핀(cordycepin)** 이라는 이름이 끼어듭니다.
생김새도, 발음도 낯설어서 “대체 뭐길래 이렇게 자주 나오지?” 싶을 때가 많습니다.

이 글은 효능을 약속하지 않습니다.
다만 **그 이름이 무엇을 가리키는지**, 왜 연구자들 사이에서 자주 등장하는지 정도만 차분히 풀어 보겠습니다.

## 코디세핀은 ‘균류에서 연구되는 한 성분’입니다

코디세핀은 *Cordyceps*속 균류에서 보고·연구되는 **화합물 이름**입니다.
논문·데이터베이스에는 `cordycepin` 또는 `3'-deoxyadenosine`으로 표기되는 경우가 많습니다.

중요한 건 여기입니다.
이름이 문헌에 나온다고 해서, 그게 곧 “우리 일상에 어떤 효능이 있다”는 뜻이 되지는 않습니다.
연구실에서 다루는 주제와, 우리가 손에 드는 **주류 제품의 이야기**는 층위가 다릅니다.

## 왜 이름이 자꾸 불릴까

동충하초를 다룰 때 사람들은 보통 세 가지를 한꺼번에 말합니다.

- **균류 자체** (*Cordyceps militaris* 같은 종)
- **추출물·배양물** 같은 원료 형태
- **코디세핀처럼 이름이 붙은 개별 성분**

세 가지를 한 문장으로 섞으면 설명이 쉬워 보이지만, 사실은 서로 다른 이야기입니다.
그래서 큐사랑 콘텐츠에서는 가능하면 이름을 **하나씩** 짚습니다.
“동충하초 = 코디세핀 = 효과”처럼 묶어 버리지 않고요.

## 주류 이야기와는 이렇게 거리를 둡니다

큐사랑의 **제왕충초 담금주**는 건강기능식품이 아니라 **주류**입니다.
성분의 이름을 소개할 수는 있어도, 그 이름을 치료·예방·체력 개선의 증거처럼 쓰면 안 됩니다.

그래서 이 시리즈의 톤은 단순합니다.

- 이름은 정확히
- 연구는 “있다 / 없다 / 어떤 단계인지” 정도만
- 제품은 **담금·장면·취향**의 언어로

효능을 크게 말하는 글보다, 이름을 바르게 쓰는 글이 더 오래 갑니다.

{refs}

{_series_nav()}

---

{d}
""".strip()


def render_militaris(cfg: dict[str, Any], refs: str) -> str:
    d = _footer(cfg)
    return f"""
“제왕충초”라는 말을 들으면, 대개 동충하초 이미지가 먼저 떠오릅니다.
그런데 동충하초라고 다 같은 생물은 아닙니다.
시중에서 한 바구니로 묶이는 이름 뒤에는, 서로 다른 종과 원료가 섞여 있을 수 있습니다.

## Cordyceps militaris를 먼저 기억하는 이유

학술·원료 맥락에서 자주 등장하는 이름 중 하나가 ***Cordyceps militaris*** 입니다.
제왕충초 이야기를 할 때 우리가 붙잡아야 할 첫 좌표도 여기에 가깝습니다.

반대로, 전통적으로 잘 알려진 *Ophiocordyceps sinensis*(예전에 Cordyceps sinensis로 불리던 계통)나
균사체 배양 원료(Cs-4 등)는 **다른 생물·다른 원료 경로**일 수 있습니다.
이름이 비슷하다고 해서 논문 한 편의 결과를 제품에 그대로 옮기면, 이야기가 어긋납니다.

## 자실체, 균사체, 추출물 — 형태도 다릅니다

같은 *militaris*라도 연구마다 재료가 다릅니다.

- 자실체(열매체처럼 보이는 형태)
- 균사체 배양물
- 추출물
- 정제된 개별 화합물(코디세핀 등)

“동충하초 연구 결과가 있다”는 문장만으로는, 위 네 가지 중 무엇을 말하는지 알 수 없습니다.
그래서 좋은 소개글은 결과를 과장하기보다, **무엇을 대상으로 한 이야기인지**를 먼저 밝힙니다.

## 제왕충초 담금주를 말할 때

큐사랑의 제왕충초 담금주는 그 이름을 **주류의 원료·장면**으로 다룹니다.
균류의 학명을 소개하는 것과, 건강상의 효능을 단정하는 것은 다른 문장입니다.

담금주 앞에서 할 수 있는 말은 오히려 단순합니다.
어디서 온 이름인지, 왜 그 이름을 붙였는지, 어떤 자리에서 함께하고 싶은지.
그게 제품 이야기의 중심이어야 합니다.

{refs}

{_series_nav()}

---

{d}
""".strip()


def render_research_literacy(cfg: dict[str, Any], refs: str) -> str:
    d = _footer(cfg)
    return f"""
코디세핀을 검색하면 논문 제목이 길게 이어집니다.
영어 초록에 강한 단어가 보이면, 그걸 곧바로 제품 소개 문장으로 옮기고 싶어지기도 합니다.

그 유혹을 참는 게, 사실 콘텐츠의 전부입니다.

## 논문이 있다고 ≠ 광고해도 된다

학술 문헌은 “연구 주제로서 다뤄졌다”는 기록에 가깝습니다.
주류 제품 블로그에서 그 기록을 **치료·예방·체력 개선**의 증거처럼 쓰면, 읽는 사람도 규제도 같이 위험해집니다.

특히 제목이나 초록에 cancer, treat, diabetes 같은 단어가 보여도
그걸 한국어 카피로 옮기는 순간, 글의 성격이 바뀝니다.

## 연구 단계를 일상어로 나누면

| 단계 | 쉽게 말하면 | 블로그에서 |
|------|-------------|------------|
| 시험관 | 세포·실험실 안의 관찰 | 메커니즘 소개 수준. 단정 금지 |
| 동물 | 실험동물 모델 | “동물 연구에서 보고” 정도만 |
| 사람 | 소규모~임상 설계 | 있어도 주류에서는 효능 문장으로 쓰지 않음 |
| 리뷰 | 여러 논문 정리 | 참고용. 골라 인용에 주의 |

표가 딱딱해 보여도, 실무에서는 이 구분이 제일 쓸모 있습니다.
“연구 결과가 있다”는 문장을 쓰기 전에, **어느 칸의 연구인지**만 물어보면 됩니다.

## 우리가 지키는 문장 규칙

1. 질병·치료·예방 단어를 제품 효능처럼 쓰지 않는다  
2. 동물·세포 결과를 사람 효과로 건너뛰지 않는다  
3. *militaris* 연구를 *sinensis* 이야기로 바꾸지 않는다  
4. “FDA 승인”, “식약처이 담금주 효능을 인정” 같은 표현은 쓰지 않는다  

규칙은 글을 작게 만들지 않습니다.
오히려 **믿을 수 있는 톤**을 남깁니다.

{refs}

{_series_nav()}

---

{d}
""".strip()


def render_regulatory(cfg: dict[str, Any], refs: str) -> str:
    d = _footer(cfg)
    return f"""
코디세핀·동충하초 이야기를 하다 보면, 규제 이름이 갑자기 끼어듭니다.
FDA, 식약처, 건강기능식품, 주류 광고…
정보가 많을수록 “뭔가 공인된 느낌”으로 포장하고 싶어지지만, 그 포장이 제일 위험합니다.

이 글은 법률 자문이 아닙니다.
다만 **자주 생기는 오해**만 먼저 걷어 내겠습니다.

## FDA에 대해 자주 생기는 착각

“논문에 나온다”와 “FDA가 치료제로 승인했다”는 완전히 다른 문장입니다.
Cordyceps·cordycepin을 다루는 많은 제품 맥락은 의약품 허가가 아니라,
식품·보충제 쪽 이야기이거나, 아예 연구 단계의 이야기에 가깝습니다.

미국에서 질병을 치료·예방·진단한다고 쓰면, 그 순간 표현의 성격이 달라질 수 있습니다.
그래서 해외 자료를 가져와 “승인된 성분”처럼 쓰는 문장은 쓰지 않습니다.

## 한국에서 더 중요한 구분

건강기능식품에 인정된 기능성 문구는 **그 유형의 제품**에만 해당합니다.
큐사랑의 제왕충초 **담금주는 주류**입니다.
HFF(건강기능식품)의 면역 기능 문구를 담금주 소개에 그대로 가져오면 안 됩니다.

주류 콘텐츠에서 특히 조심할 말은 이런 쪽입니다.

- 음주가 체력·운동에 도움이 된다
- 질병을 낫게 한다 / 예방한다
- 정신건강을 개선한다

성분 이름을 소개하는 것과, 음주를 건강 행위처럼 설명하는 것은 다릅니다.

## 그래서 우리는 이렇게 씁니다

- 성분명·균류명·연구의 존재 → 가능 (과장 없이)
- 효능 단정·질병 언어·승인 오해 → 하지 않음
- 제품 본문은 **담금, 자리, 취향**의 언어로

규제를 겁주기 위해서가 아닙니다.
오래 가는 브랜드 글은, 말할 수 있는 것과 말할 수 없는 것을 처음부터 나누기 때문입니다.

{refs}

{_series_nav()}

---

{d}
""".strip()


def render_brand(cfg: dict[str, Any], refs: str) -> str:
    d = _footer(cfg)
    return f"""
좋은 담금주는 설명이 길지 않아도 장면이 먼저 그려집니다.
누구와 앉았는지, 어떤 잔인지, 그날의 공기가 어땠는지.

큐사랑의 **제왕충초 담금주**도 그 장면 위에 있습니다.
동충하초 계열의 이름을 빌리되, 그 이름을 약처럼 포장하지 않는 쪽을 택합니다.

## 이름을 다루는 방식

제왕충초라는 이름 곁에는 *Cordyceps militaris*, 그리고 연구에서 자주 불리는 **코디세핀**이 따라붙곤 합니다.
우리는 그 이름들을 **원료와 이야기의 좌표**로 소개합니다.
좌표는 길을 알려 주지만, 목적지를 “효능”으로 바꿔 쓰지는 않습니다.

그래서 제품 소개에서 우선하는 문장은 이런 쪽입니다.

- 어떤 이름을 담았는지
- 왜 그 이름이 브랜드에 붙었는지
- 어떤 자리에서 함께하고 싶은지

반대로 이런 문장은 쓰지 않습니다.

- 항암·치료·예방을 암시하는 말
- 면역·피로를 “보장”처럼 읽는 말
- “식약처가 담금주 효능을 인정” 같은 오해

## 담금이 남기는 것

담금주는 빠른 소비보다, **시간과 자리를 나누는 술**에 가깝습니다.
제왕충초라는 이름이 있다면, 그 이름은 대화의 시작점이 되면 충분합니다.
“이게 뭐야?”에서 시작해, 균류의 이름과 성분의 이름을 짧게 짚고,
다시 잔으로 돌아오는 흐름이면 됩니다.

건강 강의가 아니라, **같이 마시는 이야기**여야 하니까요.

## 이 시리즈가 있는 이유

성분 이름을 검색하면 논문과 자극적인 요약이 먼저 나옵니다.
그 사이에서 브랜드가 할 일은 단순합니다.
정확히 말하고, 과장하지 않고, 주류답게 남기기의.

그래서 큐사랑 콘텐츠는 코디세핀·militaris·규제 오해까지 한꺼번에 정리해 둡니다.
제품을 크게 보이려는 글이 아니라, **오래 믿어도 되는 글**을 남기려는 쪽에 가깝습니다.

다음에 잔을 기울일 때, 이름이 조금 더 선명해지길 바랍니다.

{refs}

{_series_nav()}

---

미성년자 음주 금지. 지나친 음주는 건강을 해칩니다.
운전 전·임신 중 음주를 피하세요.

{d}
""".strip()


RENDERERS = {
    "ingredient_intro": render_what_is_cordycepin,
    "species_intro": render_militaris,
    "research_literacy": render_research_literacy,
    "regulatory_literacy": render_regulatory,
    "brand_product": render_brand,
}


def _meta_description(body: str) -> str:
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("|") or line.startswith(">"):
            continue
        if line.startswith("-"):
            continue
        return _clean(line)[:140]
    return "큐사랑 제왕충초 — 코디세핀과 담금의 이야기"


def _write_publish_checklist(out_dir: Path) -> None:
    text = """# 블로그 발행 체크리스트 (제왕충초)

- [ ] 본문이 ‘논문 링크 나열’이 아니라 읽히는 글인가
- [ ] 질병·치료·예방·진단 표현 없음
- [ ] “FDA 승인 / 식약처 효능 인정(담금주)” 없음
- [ ] 음주 = 건강·체력 개선처럼 읽히지 않음
- [ ] 하단에 주류 디스클레이머
- [ ] 시리즈 다른 글로 자연스럽게 이어지는가
- [ ] 법무/담당자 리뷰

WordPress: 사용 안 함. 배포: `cd web && npx vercel --prod`
"""
    (out_dir / "PUBLISH_CHECKLIST.md").write_text(text, encoding="utf-8")
    (ROOT / "docs" / "BLOG_PUBLISH_CHECKLIST.md").write_text(text, encoding="utf-8")


def export_blog() -> list[Path]:
    cfg = load_yaml("blog_series.yaml")
    records = read_jsonl(EVIDENCE_JSONL)
    refs = _further_reading(_pick_refs(records, limit=2))

    content_dir = ROOT / (cfg.get("output", {}).get("content_dir") or "content/blog")
    content_dir.mkdir(parents=True, exist_ok=True)

    vault_blog = vault_path() / "40_Blog"
    vault_blog.mkdir(parents=True, exist_ok=True)
    for p in vault_blog.glob("*.md"):
        if not p.name.startswith("_"):
            p.unlink()

    written: list[Path] = []
    index_rows: list[dict[str, str]] = []

    for post in cfg.get("series") or []:
        angle = post.get("angle") or ""
        renderer = RENDERERS.get(angle)
        if not renderer:
            continue
        body = renderer(cfg, refs)
        desc = _meta_description(body)
        content = _frontmatter(post, desc) + "\n# " + post["title"] + "\n\n" + body + "\n"
        fname = f"{post['slug']}.md"
        path = content_dir / fname
        path.write_text(content, encoding="utf-8")
        (vault_blog / fname).write_text(content, encoding="utf-8")
        written.append(path)
        index_rows.append(
            {
                "slug": post["slug"],
                "title": post["title"],
                "category": post.get("category") or "",
                "status": post.get("status") or "draft",
                "path": str(path.relative_to(ROOT)),
                "vault_path": f"40_Blog/{fname}",
                "keywords": "|".join(post.get("keywords") or []),
            }
        )

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    index_path = EXPORT_DIR / "blog_index.csv"
    with index_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["slug", "title", "category", "status", "path", "vault_path", "keywords"],
        )
        w.writeheader()
        w.writerows(index_rows)

    _write_publish_checklist(content_dir)

    index_md = [
        "# 블로그 시리즈 — 코디세핀 / 제왕충초",
        "",
        f"_Generated: {date.today().isoformat()}_",
        "",
        "본문 중심 에디토리얼. 논문 링크 나열이 아닙니다.",
        "",
        "| # | 제목 | slug |",
        "|---|------|------|",
    ]
    for i, row in enumerate(index_rows, 1):
        index_md.append(f"| {i} | {row['title']} | `{row['slug']}` |")
    index_md.extend(
        [
            "",
            "## 발행",
            "",
            "```bash",
            "cordycepin blog",
            "cd web && npx vercel --prod",
            "```",
            "",
        ]
    )
    (content_dir / "README.md").write_text("\n".join(index_md), encoding="utf-8")
    (ROOT / "docs" / "BLOG_SERIES.md").write_text("\n".join(index_md), encoding="utf-8")

    # Mirror for Vercel deploy (web/ root)
    web_blog = ROOT / "web" / "content" / "blog"
    web_blog.mkdir(parents=True, exist_ok=True)
    for path in written:
        dest = web_blog / path.name
        dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"[blog] wrote {len(written)} editorial posts -> {content_dir}")
    print(f"[blog] mirrored -> {web_blog}")
    return written


if __name__ == "__main__":
    export_blog()
