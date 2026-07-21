# measuremkt 네트워크 — WordPress ↔ Vercel 연결

| URL | 역할 |
|-----|------|
| https://measuremkt.com/ | **WordPress** — 측정하는 마케터 (GA4·GTM 가이드) |
| https://q-sarang.measuremkt.com/ | **Vercel Next.js** — 큐사랑 · 제왕충초 브랜드 사이트 |
| https://sports.measuremkt.com/ | Vercel — 스포츠 |

`q-sarang` 서브도메인에는 WordPress를 설치하지 않습니다.  
메인 WP는 **허브(링크·티저)** 역할만 하고, 본문은 Vercel 사이트에서 운영합니다.

---

## 1. DNS (Cloudflare)

Vercel이 안내한 대로 `q-sarang` 레코드를 설정합니다.

```
Type: A
Name: q-sarang
Value: 76.76.21.21
```

기존 WP 서버 IP(`183.111.138.240`) A 레코드는 **삭제**합니다.

확인:
```bash
cd web && npx vercel domains inspect q-sarang.measuremkt.com
```

---

## 2. WordPress 허브 연결 (한 번)

`.env`에 메인 WP 자격증명:
```
WP_BASE_URL=https://measuremkt.com
WP_TARGET=parent
WP_USERNAME=...
WP_APP_PASSWORD=...
```

연결 실행:
```bash
cordycepin wp-connect
```

자동 처리:
- 상단 메뉴에 **큐사랑** 링크 추가 → `q-sarang.measuremkt.com`
- 메인 사이트 허브 페이지 생성/갱신 → `/q-sarang/`

---

## 3. 블로그 티저 발행 (메인 WP)

전문은 Vercel, 메인 WP에는 요약+링크만 올립니다.

```bash
cordycepin blog
cordycepin wp-publish --target parent              # draft
cordycepin wp-publish --target parent --status publish  # 공개
```

티저 글 슬러그: `qsarang-{slug}` (예: `qsarang-what-is-cordycepin`)

---

## 4. Vercel 환경 변수

| 변수 | 값 |
|------|-----|
| `SITE_URL` | `https://q-sarang.measuremkt.com` |
| `NEXT_PUBLIC_WP_REST_URL` | `https://measuremkt.com/wp-json/wp/v2` |

메인 사이트 최신 글은 홈 하단 **Network** 섹션에서 REST로 읽습니다 (읽기 전용).

---

## 5. 상태 확인

```bash
cordycepin wp-status
```

---

## 아키텍처

```
content/blog/*.md  →  Vercel (q-sarang)  ← canonical 본문
        ↓
cordycepin wp-publish --target parent  →  measuremkt.com (티저 + 링크)
cordycepin wp-connect                  →  메뉴 + /q-sarang/ 허브 페이지
```

자세한 Vercel 배포: [web/DEPLOY.md](../web/DEPLOY.md)
