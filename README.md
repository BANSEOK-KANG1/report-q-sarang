# 큐사랑 · 제왕충초 — 코디세핀 근거 수집 파이프라인

레포의 `data/`를 단일 소스(source of truth)로 두고, PubMed / OpenAlex / Europe PMC에서 코디세핀·*Cordyceps militaris* 논문을 수집한 뒤 **근거 등급·클레임 위험**을 태깅하고 Notion·Obsidian으로 동기화합니다.

> **중요:** 제왕충초 담금주는 **주류**입니다. 논문이 있다고 해서 소비자 광고에 효능·질병 문구를 쓸 수 없습니다. `citation_status` / `maps_to_market`로 광고 가능 여부를 강제 분리합니다. 자세한 내용은 [docs/COMPLIANCE.md](docs/COMPLIANCE.md)를 보세요.

## 빠른 시작

```bash
cd report_q-sarang
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # NCBI_API_KEY, OPENALEX_EMAIL 등 입력

# 전체 파이프라인 (수집 → 정규화 → 스코어링 → Obsidian → export)
cordycepin run-all

# 단계별
cordycepin ingest
cordycepin normalize
cordycepin score
cordycepin sync-obsidian
cordycepin export
cordycepin sync-notion   # NOTION_TOKEN + NOTION_DB_ID 필요
```

## 산출물

| 경로 | 설명 |
|------|------|
| `data/normalized/evidence.jsonl` | 정규화된 근거 레코드 |
| `data/exports/marketing_safe.csv` | 승인된 주류 맥락 인용만 |
| `data/exports/research_only.csv` | 내부 R&D / 교육용 |
| `data/exports/priority_review.csv` | 검수 우선 큐 |
| `docs/MARKETING_EVIDENCE_BRIEF.md` | 마케팅 브리프 |
| `content/blog/` | 블로그 포스팅 초안 (CMS 붙여넣기용) |
| `vault/10_Evidence/` | Obsidian Evidence 노트 |
| `vault/30_Marketing_Safe/` | 승인된 인용만 |
| `vault/40_Blog/` | Obsidian 블로그 초안 미러 |

## 블로그 · 사이트 (football/sports와 동일 패턴)

큐사랑 콘텐츠는 **메인 WP가 아니라** 서브도메인 Next 사이트입니다.

| URL | 앱 |
|-----|-----|
| https://measuremkt.com/ | 측정하는 마케터 |
| https://sports.measuremkt.com/ | football 스포츠 |
| https://q-sarang.measuremkt.com/ | **큐사랑 · 제왕충초** → [`web/`](web/) |

```bash
cordycepin blog          # content/blog/*.md 생성
cd web && npm run dev    # localhost:3322
```

배포: [web/DEPLOY.md](web/DEPLOY.md) (DNS CNAME → Vercel, sports와 동일)

## 운영

검수 → 승인 프로세스는 [docs/PROCESS.md](docs/PROCESS.md)를 따릅니다.
