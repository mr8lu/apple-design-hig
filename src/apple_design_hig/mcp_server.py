"""FastMCP server for querying and syncing Apple Human Interface Guidelines."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from apple_design_hig.cli import default_skill_dir
from apple_design_hig.client import (
    get_topic_markdown,
    list_all_topics,
    search_topics,
    sync_references,
)

mcp = FastMCP("apple-design-hig")


@mcp.tool()
def hig_list_sections() -> dict[str, object]:
    """List all Apple Human Interface Guidelines sections and topics."""
    topics = list_all_topics()
    sections: dict[str, list[dict[str, str]]] = {}
    for item in topics:
        sections.setdefault(item["section"], []).append(
            {"title": item["title"], "slug": item["slug"], "url": item["url"]}
        )
    return {
        "total_topics": len(topics),
        "sections": sections,
    }


@mcp.tool()
def hig_search(query: str, section: str | None = None) -> dict[str, object]:
    """Search Apple Human Interface Guidelines topics by keyword and optional section."""
    matches = search_topics(query, section=section)
    return {
        "query": query,
        "section": section,
        "count": len(matches),
        "matches": matches[:50],
    }


@mcp.tool()
def hig_get_topic(slug: str) -> str:
    """Fetch and render the live Apple Human Interface Guidelines article for a slug (e.g. color, buttons, designing-for-ios)."""
    return get_topic_markdown(slug)


@mcp.tool()
def hig_sync() -> dict[str, object]:
    """Sync the local apple-design-hig skill reference catalog with Apple's live DocC endpoints."""
    return sync_references(default_skill_dir() / "references")


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
