"""CLI entrypoint for apple-design-hig."""

from __future__ import annotations

import argparse
import sys
import urllib.error
from pathlib import Path

from apple_design_hig.client import (
    get_topic_markdown,
    install_skill_directories,
    search_topics,
    sync_references,
)


def default_skill_dir() -> Path:
    repo_root = Path(__file__).resolve().parent.parent.parent
    return repo_root / "skills" / "apple-design-hig"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="apple-design-hig",
        description="Apple Human Interface Guidelines (HIG) skill manager, DocC sync CLI, and MCP launcher",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_topic = sub.add_parser("topic", help="Fetch and render an Apple HIG topic by slug")
    p_topic.add_argument("slug", help="Topic slug, e.g. color, typography, buttons, designing-for-ios")

    p_search = sub.add_parser("search", help="Search Apple HIG topics by keyword")
    p_search.add_argument("query", help="Search keyword")
    p_search.add_argument("--section", help="Optional section filter", default=None)

    p_sync = sub.add_parser("sync", help="Sync Apple HIG catalog and pillar references from Apple DocC API")
    p_sync.add_argument(
        "--output-dir",
        type=Path,
        default=default_skill_dir() / "references",
        help="Output directory for references",
    )

    p_install = sub.add_parser(
        "install-skill",
        help="Install/sync the apple-design-hig skill into ~/.gemini/skills and ~/.agents/skills",
    )
    p_install.add_argument(
        "--skill-dir",
        type=Path,
        default=default_skill_dir(),
        help="Path to the skill source directory",
    )

    sub.add_parser("mcp", help="Run the apple-design-hig MCP server over stdio")

    args = parser.parse_args(argv)
    if args.cmd == "topic":
        try:
            print(get_topic_markdown(args.slug))
            return 0
        except urllib.error.HTTPError as exc:
            print(f"Error: HTTP {exc.code} fetching topic '{args.slug}'", file=sys.stderr)
            return 1
    if args.cmd == "search":
        matches = search_topics(args.query, section=args.section)
        print(f"Found {len(matches)} Apple HIG topic(s) matching '{args.query}':\n")
        for item in matches[:50]:
            print(f"- **{item['title']}** (`{item['slug']}`) [{item['section']}] -> {item['url']}")
        return 0
    if args.cmd == "sync":
        summary = sync_references(args.output_dir)
        print(
            f"Success: Synced {summary['total_topics']} topics "
            f"({len(summary['synced_pillars'])} pillars) into {summary['output_dir']}"
        )
        return 0
    if args.cmd == "install-skill":
        installed = install_skill_directories(args.skill_dir)
        for dest in installed:
            print(f"Installed apple-design-hig skill to: {dest}")
        return 0
    if args.cmd == "mcp":
        from apple_design_hig.mcp_server import main as mcp_main

        mcp_main()
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
