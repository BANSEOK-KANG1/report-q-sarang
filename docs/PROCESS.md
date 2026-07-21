# 운영 프로세스 — 수집 → 검수 → 승인 → 문구

## 1. 수집 (주 1회 권장)

```bash
source .venv/bin/activate
cordycepin ingest
cordycepin normalize
cordycepin score
cordycepin sync-obsidian
cordycepin export
cordycepin blog
```

신규 레코드는 `citation_status=candidate`로 들어옵니다.

## 2. 검수 큐

1. `data/exports/priority_review.csv` 또는 Obsidian `10_Evidence`에서 `priority_review: true` 노트를 연다.
2. 확인 항목:
   - 종(*C. militaris* vs *sinensis*/Cs-4)이 제품과 맞는가
   - 연구 설계(in vitro / animal / human)가 맞는가
   - 질병·치료 언어가 abstract에 있는가 (`risk_flags`)
   - 용량·제형이 제품과 비교 가능한가
3. 상태 변경 (`evidence.jsonl` 또는 Obsidian frontmatter → 재동기화):
   - `needs_legal_review` — 질병어·고위험
   - `approved` — 사용 허용 (시장 매핑도 함께 설정)
   - `rejected` — 사용 불가

## 3. 시장 매핑 (`maps_to_market`)

| 값 | 의미 |
|----|------|
| `research_only` | 내부/교육만. 소비자 광고 금지 |
| `KR_liquor_context` | 주류 광고용 **객관 소개**만 (효능 금지). 법무 승인 후 |
| `KR_HFF_ref_only` | 건강기능식품 고시 참조용. 담금주 라벨 전용 금지 |
| `US_structure_function_ref` | 미국 structure/function 참고. FDA 승인 치료제 표현 금지 |

## 4. 마케팅 문구 · 블로그 사이트

1. `cordycepin blog` → `content/blog/` 에디토리얼 초안
2. 로컬 확인: `cd web && npm run dev` (http://localhost:3322)
3. 배포: [web/DEPLOY.md](../web/DEPLOY.md) → **q-sarang.measuremkt.com** (sports/football과 동일)
4. 메인 measuremkt.com WP에는 올리지 않음

메인([measuremkt.com](https://measuremkt.com/))은 측정 가이드, 스포츠는 sports., 큐사랑은 q-sarang. 서브도메인으로 분리합니다.

## 5. Obsidian 폴더

| 폴더 | 용도 |
|------|------|
| `00_Inbox` | 수동 메모 |
| `10_Evidence` | 전체 논문 노트 |
| `20_Regulatory` | FDA/식약처 요약 |
| `30_Marketing_Safe` | `approved` + liquor/context만 |
| `40_Blog` | 블로그 포스팅 초안 |
| `90_Templates` | 템플릿 |

## 6. Notion

`.env`에 `NOTION_TOKEN`, `NOTION_DB_ID`(또는 최초 `NOTION_PARENT_PAGE_ID`로 DB 생성)를 넣고 `cordycepin sync-notion`을 실행합니다. DOI/PMID로 upsert됩니다.
