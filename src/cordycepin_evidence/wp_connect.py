"""Connect measuremkt.com WordPress hub with q-sarang Vercel site."""

from __future__ import annotations

import json
import os
from typing import Any

import requests

from . import sync_wordpress as sw
from .utils import EXPORT_DIR, load_env, load_yaml

STATE_PATH = EXPORT_DIR / "wordpress_connect.json"


def _cfg() -> dict[str, Any]:
    return load_yaml("wordpress.yaml")


def _content_site_url() -> str:
    cfg = _cfg()
    site = cfg.get("site") or {}
    hub = cfg.get("hub") or {}
    return (
        os.getenv("SITE_URL", "").strip().rstrip("/")
        or hub.get("content_site_url", "").rstrip("/")
        or site.get("content_site_url", "").rstrip("/")
        or "https://q-sarang.measuremkt.com"
    )


def _parent_base() -> str:
    cfg = _cfg()
    return (cfg.get("site") or {}).get("parent_brand_url", "https://measuremkt.com").rstrip("/")


def load_state() -> dict[str, Any]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _api(base: str, path: str) -> str:
    return f"{base.rstrip('/')}{path}"


def ensure_menu_item(
    session: requests.Session,
    base: str,
    menu_id: int,
    title: str,
    url: str,
    state: dict[str, Any],
    dry_run: bool = False,
) -> dict[str, Any] | None:
    key = f"menu:{menu_id}:{title}"
    existing_id = (state.get("menu_items") or {}).get(key)

    if existing_id:
        r = session.get(_api(base, f"/wp-json/wp/v2/menu-items/{existing_id}"), timeout=30)
        if r.ok:
            item = r.json()
            if item.get("url") != url:
                if dry_run:
                    print(f"[wp-connect] dry-run would update menu id={existing_id} url={url}")
                else:
                    r2 = session.post(
                        _api(base, f"/wp-json/wp/v2/menu-items/{existing_id}"),
                        json={"url": url},
                        timeout=30,
                    )
                    r2.raise_for_status()
                    item = r2.json()
                    print(f"[wp-connect] menu updated id={existing_id} -> {url}")
            else:
                print(f"[wp-connect] menu ok id={existing_id} {url}")
            return item

    # search by title in menu
    r = session.get(
        _api(base, "/wp-json/wp/v2/menu-items"),
        params={"menus": menu_id, "per_page": 100},
        timeout=30,
    )
    r.raise_for_status()
    for item in r.json():
        rendered = (item.get("title") or {}).get("rendered") or ""
        if rendered == title:
            state.setdefault("menu_items", {})[key] = item["id"]
            if item.get("url") != url and not dry_run:
                session.post(
                    _api(base, f"/wp-json/wp/v2/menu-items/{item['id']}"),
                    json={"url": url},
                    timeout=30,
                )
            print(f"[wp-connect] menu found id={item['id']} {title}")
            return item

    if dry_run:
        print(f"[wp-connect] dry-run would create menu '{title}' -> {url}")
        return None

    r = session.post(
        _api(base, "/wp-json/wp/v2/menu-items"),
        json={
            "title": title,
            "status": "publish",
            "menus": menu_id,
            "type": "custom",
            "url": url,
        },
        timeout=30,
    )
    r.raise_for_status()
    item = r.json()
    state.setdefault("menu_items", {})[key] = item["id"]
    print(f"[wp-connect] menu created id={item['id']} {title} -> {url}")
    return item


def ensure_hub_page(
    session: requests.Session,
    base: str,
    content_url: str,
    state: dict[str, Any],
    dry_run: bool = False,
) -> dict[str, Any] | None:
    cfg = _cfg()
    hub = cfg.get("hub") or {}
    slug = hub.get("page_slug", "q-sarang")
    title = hub.get("page_title", "큐사랑 · 제왕충초")
    html = f"""<div class="mmkt-prose">
<p class="mmkt-lead"><strong>큐사랑 · 제왕충초</strong> 브랜드 콘텐츠는 별도 사이트에서 운영합니다.
코디세핀, <em>Cordyceps militaris</em>, 제왕충초 담금주 이야기를 과장 없이 정리합니다.</p>
<p><a class="mmkt-btn" href="{content_url}/">브랜드 사이트로 이동 →</a></p>
<p><a href="{content_url}/blog/">이야기 모음</a> ·
<a href="{content_url}/about/">소개</a> ·
<a href="{content_url}/editorial/">편집 원칙</a></p>
<hr />
<p><small>본 콘텐츠는 주류 브랜드 정보입니다. 질병의 예방·치료·진단과 무관합니다.</small></p>
</div>"""

    known_id = (state.get("hub_page") or {}).get("id")
    if known_id:
        r = session.get(_api(base, f"/wp-json/wp/v2/pages/{known_id}"), timeout=30)
        if r.ok:
            if dry_run:
                print(f"[wp-connect] dry-run would update hub page id={known_id}")
                return r.json()
            r2 = session.post(
                _api(base, f"/wp-json/wp/v2/pages/{known_id}"),
                json={"title": title, "content": html, "status": "publish"},
                timeout=60,
            )
            r2.raise_for_status()
            page = r2.json()
            print(f"[wp-connect] hub page updated id={page['id']} {page.get('link')}")
            state["hub_page"] = {"id": page["id"], "link": page.get("link"), "slug": slug}
            return page

    r = session.get(
        _api(base, "/wp-json/wp/v2/pages"),
        params={"slug": slug, "status": "any"},
        timeout=30,
    )
    r.raise_for_status()
    items = r.json()
    if items:
        page = items[0]
        if dry_run:
            print(f"[wp-connect] dry-run would update existing page id={page['id']}")
            return page
        r2 = session.post(
            _api(base, f"/wp-json/wp/v2/pages/{page['id']}"),
            json={"title": title, "content": html, "status": "publish"},
            timeout=60,
        )
        r2.raise_for_status()
        page = r2.json()
    elif dry_run:
        print(f"[wp-connect] dry-run would create hub page slug={slug}")
        return None
    else:
        r = session.post(
            _api(base, "/wp-json/wp/v2/pages"),
            json={"title": title, "slug": slug, "content": html, "status": "publish"},
            timeout=60,
        )
        r.raise_for_status()
        page = r.json()
        print(f"[wp-connect] hub page created id={page['id']} {page.get('link')}")

    state["hub_page"] = {"id": page["id"], "link": page.get("link"), "slug": slug}
    return page


def wp_connect(dry_run: bool = False) -> int:
    load_env()
    cfg = _cfg()
    hub = cfg.get("hub") or {}
    base = _parent_base()
    content_url = _content_site_url()
    menu_id = int(hub.get("menu_id", 7))
    menu_title = hub.get("menu_title", "큐사랑")

    print(f"[wp-connect] parent={base}")
    print(f"[wp-connect] content_site={content_url}")

    state = load_state()
    if dry_run:
        print("[wp-connect] dry-run")
        print(f"[wp-connect] would ensure menu '{menu_title}' -> {content_url}/")
        print(f"[wp-connect] would ensure hub page slug={hub.get('page_slug', 'q-sarang')}")
        return 0

    sw._ACTIVE_TARGET = "parent"
    session = sw._session()
    me = sw.ping(session)
    print(f"[wp-connect] authenticated as {me.get('name') or me.get('slug')}")

    ensure_menu_item(session, base, menu_id, menu_title, f"{content_url}/", state)
    ensure_hub_page(session, base, content_url, state)
    save_state(state)
    print(f"[wp-connect] state -> {STATE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(wp_connect())
