"""Check DNS/SSL/REST readiness for WordPress publish target."""

from __future__ import annotations

import os
import socket
import ssl
from typing import Any
from urllib.parse import urlparse

import requests

from .utils import load_env, load_yaml


def _check_dns(host: str) -> dict[str, Any]:
    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        ips = sorted({i[4][0] for i in infos})
        return {"ok": True, "ips": ips}
    except socket.gaierror as e:
        return {"ok": False, "error": str(e), "ips": []}


def _check_ssl(host: str) -> dict[str, Any]:
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                return {
                    "ok": True,
                    "subject": cert.get("subject"),
                    "issuer": cert.get("issuer"),
                }
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


def _check_rest(base: str) -> dict[str, Any]:
    try:
        r = requests.get(f"{base.rstrip('/')}/wp-json/", timeout=15)
        if not r.ok:
            return {"ok": False, "status": r.status_code, "body": r.text[:200]}
        data = r.json()
        return {
            "ok": True,
            "name": data.get("name"),
            "url": data.get("home") or data.get("url"),
            "namespaces": (data.get("namespaces") or [])[:8],
        }
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


def wp_status() -> int:
    load_env()
    cfg = load_yaml("wordpress.yaml")
    base = os.getenv("WP_BASE_URL", "").strip() or (cfg.get("site") or {}).get("base_url", "")
    base = base.rstrip("/")
    host = urlparse(base).hostname or ""
    parent = (cfg.get("site") or {}).get("parent_brand_url", "https://measuremkt.com")

    print(f"[wp-status] target = {base}")
    print(f"[wp-status] parent = {parent}")

    dns = _check_dns(host)
    print(f"[wp-status] DNS  = {'OK' if dns.get('ok') else 'FAIL'} {dns}")

    ssl_r = _check_ssl(host) if dns.get("ok") else {"ok": False, "error": "skipped (no DNS)"}
    print(f"[wp-status] SSL  = {'OK' if ssl_r.get('ok') else 'FAIL'} {ssl_r.get('error') or 'cert ok'}")

    rest = _check_rest(base) if ssl_r.get("ok") else {"ok": False, "error": "skipped (no SSL)"}
    print(f"[wp-status] REST = {'OK' if rest.get('ok') else 'FAIL'} {rest}")

    user = bool(os.getenv("WP_USERNAME", "").strip())
    app = bool(os.getenv("WP_APP_PASSWORD", "").strip())
    print(f"[wp-status] ENV  = WP_USERNAME={'set' if user else 'MISSING'} WP_APP_PASSWORD={'set' if app else 'MISSING'}")

    parent_rest = _check_rest(parent)
    print(f"[wp-status] parent REST = {'OK' if parent_rest.get('ok') else 'FAIL'} name={parent_rest.get('name')}")

    ready = bool(dns.get("ok") and ssl_r.get("ok") and rest.get("ok") and user and app)
    if ready:
        print("[wp-status] READY — run: cordycepin wp-publish")
        return 0

    print("\n[wp-status] NOT READY — next steps:")
    if not dns.get("ok"):
        print("  1) DNS: add A/CNAME for q-sarang → same IP as measuremkt.com")
    elif not ssl_r.get("ok"):
        print("  1) SSL: issue certificate for q-sarang.measuremkt.com on the host (SNI)")
        print("     Cafe24/가비아 등: 서브도메인 추가 + SSL 발급 + 가상호스트/워드프레스 연결")
    elif not rest.get("ok"):
        print("  1) Install WordPress on the subdomain (or Multisite site)")
        print("  2) Settings → Permalinks → Post name → Save")
    if not user or not app:
        print("  • Add WP_USERNAME + WP_APP_PASSWORD to .env (Application Password)")
    print("  • Full guide: docs/WORDPRESS_SETUP.md")
    if parent_rest.get("ok") and (not rest.get("ok")):
        print("\n  Interim option: publish to measuremkt.com category instead:")
        print("    WP_BASE_URL=https://measuremkt.com cordycepin wp-publish")
        print("    (set credentials for measuremkt.com admin first)")
    return 1


if __name__ == "__main__":
    raise SystemExit(wp_status())
