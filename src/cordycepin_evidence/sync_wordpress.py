"""Publish blog Markdown drafts to WordPress via REST API."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import requests
import yaml
from requests.auth import HTTPBasicAuth

from .utils import EXPORT_DIR, ROOT, load_env, load_yaml

STATE_PATH = EXPORT_DIR / "wordpress_posts.json"
BLOG_DIR = ROOT / "content" / "blog"


def _cfg() -> dict[str, Any]:
    return load_yaml("wordpress.yaml")


def _base_url(target: str | None = None) -> str:
    load_env()
    cfg = _cfg()
    site = cfg.get("site") or {}
    override = os.getenv("WP_BASE_URL", "").strip().rstrip("/")
    env_target = (target or os.getenv("WP_TARGET", "") or "").strip().lower()

    if override and env_target not in ("parent", "subdomain"):
        return override
    if env_target == "parent":
        return (site.get("parent_brand_url") or "https://measuremkt.com").rstrip("/")
    if env_target == "subdomain":
        return (site.get("base_url") or "").rstrip("/")
    return (site.get("base_url") or override or "").rstrip("/")


# module-level target set by sync_wordpress
_ACTIVE_TARGET: str | None = None


def _resolve_base() -> str:
    return _base_url(_ACTIVE_TARGET)


def _credentials() -> tuple[str, str]:
    load_env()
    user = os.getenv("WP_USERNAME", "").strip().strip("'\"")
    password = os.getenv("WP_APP_PASSWORD", "").strip().strip("'\"")
    if not user or not password:
        raise SystemExit(
            "WP_USERNAME / WP_APP_PASSWORD missing in .env\n"
            "See docs/WORDPRESS_SETUP.md"
        )
    return user, password.replace(" ", "")


def _extract_nonce(html: str) -> str | None:
    m = re.search(r'wpApiSettings\s*=\s*\{[^}]*"nonce"\s*:\s*"([a-zA-Z0-9]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'"nonce"\s*:\s*"([a-zA-Z0-9]+)"', html)
    return m.group(1) if m else None


def _cookie_login(session: requests.Session, user: str, password: str) -> str:
    """Log in via wp-login.php and return REST nonce."""
    base = _resolve_base()
    session.get(f"{base}/wp-login.php", timeout=30)
    r = session.post(
        f"{base}/wp-login.php",
        data={
            "log": user,
            "pwd": password,
            "wp-submit": "Log In",
            "redirect_to": f"{base}/wp-admin/",
            "testcookie": "1",
        },
        headers={"Referer": f"{base}/wp-login.php"},
        allow_redirects=True,
        timeout=30,
    )
    if "wp-admin" not in (r.url or "") and "wordpress_logged_in" not in session.cookies.get_dict():
        raise SystemExit("WordPress web login failed. Check WP_USERNAME / password.")
    admin = session.get(f"{base}/wp-admin/", timeout=30)
    nonce = _extract_nonce(admin.text)
    if not nonce:
        # fallback: create post screen often embeds api settings
        edit = session.get(f"{base}/wp-admin/post-new.php", timeout=30)
        nonce = _extract_nonce(edit.text)
    if not nonce:
        raise SystemExit("Could not extract WP REST nonce from wp-admin.")
    session.headers["X-WP-Nonce"] = nonce
    return nonce


def _try_create_app_password(session: requests.Session) -> str | None:
    """Create Application Password for future Basic Auth (best effort)."""
    r = session.post(
        _api("/wp-json/wp/v2/users/me/application-passwords"),
        json={"name": "q-sarang-pipeline"},
        timeout=30,
    )
    if not r.ok:
        return None
    data = r.json()
    pw = data.get("password")
    if not pw:
        return None
    # Persist for next runs (do not print)
    env_path = ROOT / ".env"
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
        out = []
        replaced = False
        for ln in lines:
            if ln.startswith("WP_APP_PASSWORD="):
                out.append(f'WP_APP_PASSWORD="{pw}"')
                replaced = True
            elif ln.startswith("WP_LOGIN_PASSWORD="):
                continue
            else:
                out.append(ln)
        if not replaced:
            out.append(f'WP_APP_PASSWORD="{pw}"')
        # keep original login password separately if missing
        env_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("[wp] created Application Password and saved to .env as WP_APP_PASSWORD")
    return pw


def _session() -> requests.Session:
    user, password = _credentials()
    s = requests.Session()
    s.headers.update({"User-Agent": "q-sarang-cordycepin-pipeline/0.1"})

    # 1) Try Basic Auth (Application Password)
    s.auth = HTTPBasicAuth(user, password)
    probe = s.get(_api("/wp-json/wp/v2/users/me"), timeout=30)
    if probe.ok:
        print("[wp] auth=basic (application password / API password)")
        return s

    # 2) Fallback: cookie login + nonce (account password)
    print("[wp] basic auth failed — trying cookie login + REST nonce")
    s.auth = None
    _cookie_login(s, user, password)
    probe2 = s.get(_api("/wp-json/wp/v2/users/me"), timeout=30)
    if not probe2.ok:
        raise SystemExit(
            f"WordPress cookie REST auth failed ({probe2.status_code}). "
            "Create an Application Password in WP Admin → Users → Profile."
        )
    print("[wp] auth=cookie+nonce")
    # Best effort: mint Application Password for next time
    try:
        new_pw = _try_create_app_password(s)
        if new_pw:
            s.auth = HTTPBasicAuth(user, new_pw.replace(" ", ""))
            # keep nonce too
    except Exception:  # noqa: BLE001
        pass
    return s


def load_state() -> dict[str, Any]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"posts": {}}


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_markdown_file(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = yaml.safe_load(parts[1]) or {}
    body = parts[2].lstrip("\n")
    # Drop duplicate H1 if same as title (WP theme adds title)
    title = (meta.get("title") or "").strip()
    lines = body.splitlines()
    if lines and lines[0].startswith("# "):
        h1 = lines[0][2:].strip()
        if not title or h1 == title:
            body = "\n".join(lines[1:]).lstrip("\n")
    return meta, body


def md_to_html(md: str) -> str:
    try:
        import markdown as md_lib
    except ImportError as e:
        raise SystemExit("Install markdown: pip install markdown") from e
    return md_lib.markdown(
        md,
        extensions=["extra", "sane_lists", "smarty", "tables"],
        output_format="html5",
    )


def _api(path: str) -> str:
    return f"{_resolve_base()}{path}"


def ping(session: requests.Session) -> dict[str, Any]:
    r = session.get(_api("/wp-json/wp/v2/users/me"), timeout=30)
    if r.status_code == 401:
        raise SystemExit("WordPress auth failed (401). Check WP_USERNAME / WP_APP_PASSWORD.")
    if r.status_code == 404:
        raise SystemExit(
            f"REST API not found at {_resolve_base()}. "
            "Is WordPress live with permalinks enabled? See docs/WORDPRESS_SETUP.md"
        )
    r.raise_for_status()
    return r.json()

def ensure_term(
    session: requests.Session,
    taxonomy: str,
    name: str,
    cache: dict[str, int],
) -> int | None:
    if not name:
        return None
    if name in cache:
        return cache[name]
    # search existing
    r = session.get(
        _api(f"/wp-json/wp/v2/{taxonomy}"),
        params={"search": name, "per_page": 100},
        timeout=30,
    )
    r.raise_for_status()
    for item in r.json():
        if item.get("name") == name:
            cache[name] = int(item["id"])
            return cache[name]
    # create
    r = session.post(
        _api(f"/wp-json/wp/v2/{taxonomy}"),
        json={"name": name},
        timeout=30,
    )
    if r.status_code in (200, 201):
        cache[name] = int(r.json()["id"])
        return cache[name]
    # term may already exist (race) — try slug search
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    r2 = session.get(
        _api(f"/wp-json/wp/v2/{taxonomy}"),
        params={"slug": slug},
        timeout=30,
    )
    if r2.ok and r2.json():
        cache[name] = int(r2.json()[0]["id"])
        return cache[name]
    print(f"[wp] warn: could not ensure {taxonomy} '{name}': {r.status_code} {r.text[:200]}")
    return None


def find_post_by_slug(session: requests.Session, slug: str) -> dict[str, Any] | None:
    r = session.get(
        _api("/wp-json/wp/v2/posts"),
        params={"slug": slug, "status": "any", "context": "edit"},
        timeout=30,
    )
    if r.status_code == 401:
        # fallback without edit context
        r = session.get(
            _api("/wp-json/wp/v2/posts"),
            params={"slug": slug, "status": "publish,draft,pending,future,private"},
            timeout=30,
        )
    r.raise_for_status()
    items = r.json()
    return items[0] if items else None


def build_payload(
    meta: dict[str, Any],
    body_md: str,
    status: str,
    cat_ids: list[int],
    tag_ids: list[int],
) -> dict[str, Any]:
    cfg = _cfg()
    hub = cfg.get("hub") or {}
    site = cfg.get("site") or {}
    pub = cfg.get("publish") or {}
    slug = meta.get("slug") or ""
    excerpt = meta.get("description") or ""
    content_url = (
        os.getenv("SITE_URL", "").strip().rstrip("/")
        or hub.get("content_site_url", "").rstrip("/")
        or site.get("content_site_url", "").rstrip("/")
        or "https://q-sarang.measuremkt.com"
    )
    article_url = f"{content_url}/blog/{slug}"

    # Parent hub: teaser + link to Vercel canonical article
    use_teaser = (
        hub.get("teaser_mode", False)
        and _ACTIVE_TARGET == "parent"
    )
    if use_teaser:
        html = (
            f'<p class="mmkt-lead">{excerpt}</p>'
            f'<p><a class="mmkt-btn" href="{article_url}">전문 읽기 →</a></p>'
            f'<p><small>본문은 <a href="{content_url}/">q-sarang.measuremkt.com</a>에서 운영합니다.</small></p>'
        )
    else:
        html = md_to_html(body_md)

    if (cfg.get("compliance") or {}).get("append_disclaimer", True):
        footer = (cfg.get("compliance") or {}).get("footer_html") or ""
        html = html + "\n" + footer
    return {
        "title": meta.get("title") or slug,
        "slug": f"qsarang-{slug}" if use_teaser else slug,
        "status": status,
        "content": html,
        "excerpt": excerpt,
        "categories": cat_ids,
        "tags": tag_ids,
    }


def publish_one(
    session: requests.Session,
    path: Path,
    status: str,
    cat_cache: dict[str, int],
    tag_cache: dict[str, int],
    state: dict[str, Any],
    dry_run: bool = False,
) -> dict[str, Any]:
    cfg = _cfg()
    pub = cfg.get("publish") or {}
    meta, body = parse_markdown_file(path)
    slug = meta.get("slug") or path.stem
    meta["slug"] = slug

    # categories / tags
    cat_map = pub.get("category_map") or {}
    cat_name = cat_map.get(meta.get("category") or "", "제왕충초")
    cat_id = ensure_term(session, "categories", cat_name, cat_cache) if not dry_run else None
    tag_names = list(dict.fromkeys((pub.get("default_tags") or []) + (meta.get("keywords") or [])))
    tag_ids: list[int] = []
    if not dry_run:
        for name in tag_names:
            tid = ensure_term(session, "tags", str(name), tag_cache)
            if tid:
                tag_ids.append(tid)

    payload = build_payload(
        meta,
        body,
        status,
        [cat_id] if cat_id else [],
        tag_ids,
    )

    if dry_run:
        print(f"[wp] dry-run would upsert slug={slug} status={status} file={path.name}")
        return {"slug": slug, "dry_run": True}

    existing = None
    if pub.get("upsert_by_slug", True):
        wp_slug = payload.get("slug") or slug
        existing = find_post_by_slug(session, wp_slug)
        if not existing:
            known_id = (state.get("posts") or {}).get(slug, {}).get("id")
            if known_id:
                r = session.get(_api(f"/wp-json/wp/v2/posts/{known_id}"), timeout=30)
                if r.ok:
                    existing = r.json()

    if existing:
        pid = existing["id"]
        r = session.post(_api(f"/wp-json/wp/v2/posts/{pid}"), json=payload, timeout=60)
        action = "updated"
    else:
        r = session.post(_api("/wp-json/wp/v2/posts"), json=payload, timeout=60)
        action = "created"

    if not r.ok:
        raise RuntimeError(f"WP {action} failed for {slug}: {r.status_code} {r.text[:400]}")

    post = r.json()
    state.setdefault("posts", {})[slug] = {
        "id": post.get("id"),
        "link": post.get("link"),
        "status": post.get("status"),
        "modified": post.get("modified"),
        "source_file": str(path.relative_to(ROOT)),
    }
    print(f"[wp] {action} id={post.get('id')} {post.get('link')} ({post.get('status')})")
    return post


def list_blog_files(slug: str | None = None) -> list[Path]:
    files = sorted(
        p
        for p in BLOG_DIR.glob("*.md")
        if p.name not in ("README.md", "PUBLISH_CHECKLIST.md")
    )
    if slug:
        files = [p for p in files if p.stem == slug]
        if not files:
            raise SystemExit(f"No blog file for slug={slug} in {BLOG_DIR}")
    return files


def sync_wordpress(
    status: str | None = None,
    slug: str | None = None,
    dry_run: bool = False,
    target: str | None = None,
) -> int:
    global _ACTIVE_TARGET
    load_env()
    cfg = _cfg()
    _ACTIVE_TARGET = (target or os.getenv("WP_TARGET") or "").strip().lower() or None

    if not _resolve_base():
        raise SystemExit("WP_BASE_URL / site.base_url missing")

    default_status = (cfg.get("publish") or {}).get("default_status", "draft")
    status = status or default_status
    if status not in ("draft", "publish", "pending", "private"):
        raise SystemExit(f"Invalid status: {status}")

    # Ensure blog files exist
    if not list_blog_files():
        from .export_blog import export_blog

        export_blog()

    state = load_state()
    cat_cache: dict[str, int] = {}
    tag_cache: dict[str, int] = {}
    base = _resolve_base()

    if dry_run:
        print(f"[wp] dry-run target={base} status={status}")
        for path in list_blog_files(slug):
            meta, _body = parse_markdown_file(path)
            print(
                f"[wp] dry-run would upsert slug={meta.get('slug') or path.stem} "
                f"file={path.name}"
            )
        return len(list_blog_files(slug))

    session = _session()
    me = ping(session)
    print(f"[wp] authenticated as {me.get('name') or me.get('slug')} @ {base}")

    n = 0
    for path in list_blog_files(slug):
        publish_one(session, path, status, cat_cache, tag_cache, state, dry_run=False)
        n += 1
    save_state(state)
    print(f"[wp] state -> {STATE_PATH}")
    return n


if __name__ == "__main__":
    sync_wordpress()
