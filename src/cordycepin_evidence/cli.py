"""CLI entrypoint: cordycepin <command>."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cordycepin",
        description="Cordycepin evidence pipeline for Q-Sarang 제왕충초",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ingest", help="Fetch PubMed + OpenAlex + Europe PMC")
    sub.add_parser("normalize", help="Deduplicate into evidence.jsonl")
    sub.add_parser("score", help="Tag study type, risks, market mapping")
    sub.add_parser("sync-obsidian", help="Write Obsidian markdown notes")
    p_notion = sub.add_parser("sync-notion", help="Upsert Notion database")
    p_notion.add_argument("--limit", type=int, default=None)
    sub.add_parser("export", help="CSV exports + marketing brief")
    sub.add_parser("blog", help="Generate blog-ready post drafts + checklist")
    sub.add_parser(
        "research",
        help="Generate per-paper research insight pages (Korean summary + abstract)",
    )
    p_wp = sub.add_parser(
        "wp-publish",
        help="Upsert blog drafts to WordPress (q-sarang.measuremkt.com)",
    )
    p_wp.add_argument(
        "--status",
        choices=["draft", "publish", "pending", "private"],
        default=None,
        help="Post status (default: draft from config)",
    )
    p_wp.add_argument("--slug", default=None, help="Publish only this slug")
    p_wp.add_argument(
        "--target",
        choices=["subdomain", "parent"],
        default=None,
        help="subdomain=q-sarang.measuremkt.com, parent=measuremkt.com",
    )
    p_wp.add_argument(
        "--dry-run",
        action="store_true",
        help="List actions without calling WordPress",
    )
    sub.add_parser(
        "wp-status",
        help="Check DNS/SSL/REST/.env readiness for WordPress target",
    )
    p_connect = sub.add_parser(
        "wp-connect",
        help="Link measuremkt.com WP hub menu + landing page to Vercel site",
    )
    p_connect.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned actions without calling WordPress",
    )
    sub.add_parser("run-all", help="ingest → normalize → score → obsidian → export → blog")
    sub.add_parser("seed-regulatory", help="Write regulatory seed notes to vault")

    args = parser.parse_args(argv)

    from .utils import ensure_dirs, load_env

    load_env()
    ensure_dirs()

    if args.cmd == "ingest":
        from .ingest_europepmc import ingest_europepmc
        from .ingest_openalex import ingest_openalex
        from .ingest_pubmed import ingest_pubmed

        ingest_pubmed()
        ingest_openalex()
        ingest_europepmc()
        return 0

    if args.cmd == "normalize":
        from .normalize import normalize

        normalize()
        return 0

    if args.cmd == "score":
        from .score_evidence import score_all

        score_all()
        return 0

    if args.cmd == "sync-obsidian":
        from .sync_obsidian import sync_obsidian, write_regulatory_seeds

        write_regulatory_seeds()
        sync_obsidian()
        return 0

    if args.cmd == "sync-notion":
        from .sync_notion import sync_notion

        sync_notion(limit=args.limit)
        return 0

    if args.cmd == "export":
        from .export_marketing_pack import export_marketing_pack

        export_marketing_pack()
        return 0

    if args.cmd == "blog":
        from .export_blog import export_blog

        export_blog()
        return 0

    if args.cmd == "research":
        from .export_research_insights import export_research_insights

        export_research_insights()
        return 0

    if args.cmd == "wp-publish":
        from .sync_wordpress import sync_wordpress

        sync_wordpress(
            status=args.status,
            slug=args.slug,
            dry_run=args.dry_run,
            target=args.target,
        )
        return 0

    if args.cmd == "wp-status":
        from .wp_status import wp_status

        return wp_status()

    if args.cmd == "wp-connect":
        from .wp_connect import wp_connect

        wp_connect(dry_run=args.dry_run)
        return 0

    if args.cmd == "seed-regulatory":
        from .sync_obsidian import write_regulatory_seeds

        write_regulatory_seeds()
        return 0

    if args.cmd == "run-all":
        from .export_blog import export_blog
        from .export_marketing_pack import export_marketing_pack
        from .export_research_insights import export_research_insights
        from .ingest_europepmc import ingest_europepmc
        from .ingest_openalex import ingest_openalex
        from .ingest_pubmed import ingest_pubmed
        from .normalize import normalize
        from .score_evidence import score_all
        from .sync_obsidian import sync_obsidian, write_regulatory_seeds

        ingest_pubmed()
        ingest_openalex()
        ingest_europepmc()
        normalize()
        score_all()
        write_regulatory_seeds()
        sync_obsidian()
        export_marketing_pack()
        export_blog()
        export_research_insights()
        print("[run-all] done. Optional: cordycepin sync-notion | cordycepin wp-publish")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
