# q-sarang.measuremkt.com 배포 가이드

[football / sports](https://sports.measuremkt.com)와 같은 방식입니다.
메인 [measuremkt.com](https://measuremkt.com/)(GA4·GTM)과 **분리된 Next.js 사이트**를 서브도메인에 올립니다.

| URL | 용도 |
|-----|------|
| https://measuremkt.com/ | 측정하는 마케터 (기존 WP) |
| https://sports.measuremkt.com/ | 스포츠 블로그 (football 앱) |
| **https://q-sarang.measuremkt.com/** | 큐사랑 · 제왕충초 (이 앱) |

글 원본은 모노레포 `content/blog/*.md` → 이 사이트가 읽어서 렌더링합니다.
메인 WP에 글을 올리지 않습니다.

---

## 1. Vercel 연결

```bash
cd web
npm install
npx vercel          # 또는 대시보드 Import
```

프로젝트 이름 예: `measuremkt-q-sarang`

### 환경 변수 (Production)

| 변수 | 값 |
|------|-----|
| `SITE_URL` | `https://q-sarang.measuremkt.com` |
| `SITE_NAME` | `큐사랑 · 제왕충초` |
| `SITE_PARENT_URL` | `https://measuremkt.com` |
| `SITE_AUTHOR` | `강반석` |
| `SITE_CONTACT_EMAIL` | `kangbs2486@gmail.com` |

Root Directory를 `web`으로 설정하세요 (레포가 report_q-sarang인 경우).
빌드 시 `../content/blog`를 읽으므로 **모노레포 루트를 포함**해 배포하거나, Vercel Root = 레포 루트 + `cd web && npm run build` 설정을 사용합니다.

권장 `vercel.json` (레포 루트 또는 web):

```json
{
  "framework": "nextjs",
  "installCommand": "cd web && npm install",
  "buildCommand": "cd web && npm run build",
  "outputDirectory": "web/.next"
}
```

또는 Vercel 프로젝트 Root Directory = `web` 이고, 상위 `content/`를 포함하도록:

```ts
// posts.ts already reads ../content/blog from web/
```

Vercel에서 Root = `web`이면 상위 폴더가 배포에 포함됩니다(기본).

---

## 2. DNS (Cloudflare — measuremkt.com)

현재 `q-sarang`은 WP 서버 IP(A)로 붙어 있으면 **삭제**하고 Vercel로 바꿉니다.
sports와 동일하게:

**권장 (Vercel이 안내한 값):**
```
Type: A
Name: q-sarang
Value: 76.76.21.21
```

또는 sports처럼 CNAME:
```
Type: CNAME
Name: q-sarang
Value: cname.vercel-dns.com
```

Cloudflare 대시보드 → measuremkt.com → DNS → 기존 `q-sarang` A(183.111.138.240) 삭제 후 위 레코드 추가.

확인:
```bash
cd web && npx vercel domains inspect q-sarang.measuremkt.com
```

---

## 3. 로컬

```bash
cd web
npm install
npm run dev
# http://localhost:3322
```

글 수정:

```bash
# 레포 루트
cordycepin blog
# web이 content/blog를 다시 읽음
```

---

## 4. 메인 사이트 네비 (선택)

measuremkt.com에 링크 추가:

```html
<a href="https://q-sarang.measuremkt.com">큐사랑</a>
```

---

## 5. 메인 WP에 올렸던 draft

실수로 measuremkt.com WP에 올린 제왕충초 draft는 **삭제**하고,
이 서브도메인 사이트만 사용합니다.
