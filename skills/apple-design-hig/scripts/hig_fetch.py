#!/usr/bin/env python3
"""Fetch, search, and sync Apple Human Interface Guidelines via Apple's official DocC JSON API."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

INDEX_URL = "https://developer.apple.com/tutorials/data/index/design--human-interface-guidelines"
TOPIC_BASE_URL = "https://developer.apple.com/tutorials/data/design/human-interface-guidelines"
WEB_BASE_URL = "https://developer.apple.com/design/human-interface-guidelines"


def fetch_json(url: str, timeout: float = 20.0) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "apple-design-hig-skill/1.0 (+https://github.com/mr8lu/apple-design-hig)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def render_inline(inline_items: list[dict[str, Any]], references: dict[str, Any]) -> str:
    parts: list[str] = []
    for item in inline_items:
        itype = item.get("type")
        if itype == "text":
            parts.append(item.get("text", "").replace("\u2014", " - ").replace("\u2013", "-"))
        elif itype == "codeVoice":
            parts.append(f"`{item.get('code', '')}`")
        elif itype in ("emphasis", "italics"):
            inner = render_inline(item.get("inlineContent", []), references)
            parts.append(f"*{inner}*")
        elif itype in ("strong", "inlineHead"):
            inner = render_inline(item.get("inlineContent", []), references)
            parts.append(f"**{inner}**")
        elif itype == "reference":
            ident = item.get("identifier", "")
            ref = references.get(ident, {})
            title = ref.get("title") or ident.rsplit("/", 1)[-1]
            url = ref.get("url", "")
            if url.startswith("/"):
                url = f"https://developer.apple.com{url}"
            parts.append(f"[{title}]({url})" if url else title)
        elif itype == "image":
            ident = item.get("identifier", "")
            ref = references.get(ident, {})
            alt = ref.get("alt") or ident
            parts.append(f"[Image: {alt}]")
        else:
            if "inlineContent" in item:
                parts.append(render_inline(item["inlineContent"], references))
            elif "text" in item:
                parts.append(str(item["text"]))
    return "".join(parts)


def render_blocks(blocks: list[dict[str, Any]], references: dict[str, Any], indent: str = "") -> list[str]:
    lines: list[str] = []
    for block in blocks:
        btype = block.get("type")
        if btype == "heading":
            level = min(max(int(block.get("level", 2)), 1), 6)
            text = block.get("text", "").replace("\u2014", " - ")
            lines.append(f"{'#' * level} {text}")
            lines.append("")
        elif btype == "paragraph":
            text = render_inline(block.get("inlineContent", []), references).strip()
            if text:
                lines.append(f"{indent}{text}")
                lines.append("")
        elif btype in ("unorderedList", "orderedList"):
            for idx, item in enumerate(block.get("items", []), start=1):
                prefix = f"{idx}. " if btype == "orderedList" else "- "
                sub_lines = render_blocks(item.get("content", []), references, indent="")
                non_empty = [ln for ln in sub_lines if ln.strip()]
                if non_empty:
                    lines.append(f"{indent}{prefix}{non_empty[0]}")
                    for extra in non_empty[1:]:
                        lines.append(f"{indent}  {extra}")
            lines.append("")
        elif btype == "aside":
            style = block.get("name") or block.get("style") or "Note"
            aside_lines = render_blocks(block.get("content", []), references)
            non_empty = [ln for ln in aside_lines if ln.strip()]
            if non_empty:
                lines.append(f"> **{style}**: {non_empty[0]}")
                for extra in non_empty[1:]:
                    lines.append(f"> {extra}")
                lines.append("")
        elif btype == "codeListing":
            syntax = block.get("syntax", "")
            code = "\n".join(block.get("code", []))
            lines.append(f"```{syntax}")
            lines.append(code)
            lines.append("```")
            lines.append("")
        elif btype == "row":
            for col in block.get("columns", []):
                col_lines = render_blocks(col.get("content", []), references, indent=indent)
                lines.extend(col_lines)
        elif btype == "table":
            rows = block.get("rows", [])
            if rows:
                rendered_rows: list[list[str]] = []
                for row in rows:
                    rendered_cells: list[str] = []
                    for cell in row:
                        cell_lines = render_blocks(cell, references)
                        cell_text = " ".join(ln.strip() for ln in cell_lines if ln.strip()).replace("|", "\\|")
                        rendered_cells.append(cell_text)
                    rendered_rows.append(rendered_cells)
                if rendered_rows:
                    header = rendered_rows[0]
                    lines.append("| " + " | ".join(header) + " |")
                    lines.append("| " + " | ".join("---" for _ in header) + " |")
                    for r in rendered_rows[1:]:
                        lines.append("| " + " | ".join(r) + " |")
                    lines.append("")
        elif btype == "links":
            for ident in block.get("items", []):
                ref = references.get(ident, {})
                title = ref.get("title") or ident.rsplit("/", 1)[-1]
                url = ref.get("url", "")
                slug = url.rsplit("/", 1)[-1] if url else ""
                abstract = render_inline(ref.get("abstract", []), references).strip()
                lines.append(f"- **{title}** (`{slug}`): {abstract}")
            lines.append("")
    return lines


def render_topic_markdown(data: dict[str, Any], slug: str) -> str:
    references = data.get("references", {})
    title = data.get("metadata", {}).get("title") or slug
    role_heading = data.get("metadata", {}).get("roleHeading", "Apple Human Interface Guidelines")
    abstract = render_inline(data.get("abstract", []), references).strip()
    out: list[str] = [
        f"# {title}",
        "",
        f"- **Category**: {role_heading}",
        f"- **Slug**: `{slug}`",
        f"- **Official URL**: {WEB_BASE_URL}/{slug}",
        "",
    ]
    if abstract:
        out.extend([f"**Summary**: {abstract}", ""])
    for section in data.get("primaryContentSections", []):
        if section.get("kind") == "content":
            out.extend(render_blocks(section.get("content", []), references))
    topic_sections = data.get("topicSections", [])
    if topic_sections:
        out.append("## Topics")
        out.append("")
        for tsec in topic_sections:
            t_title = tsec.get("title") or tsec.get("anchor") or "Subtopics"
            out.append(f"### {t_title}")
            out.append("")
            for ident in tsec.get("identifiers", []):
                ref = references.get(ident, {})
                r_title = ref.get("title") or ident.rsplit("/", 1)[-1]
                r_url = ref.get("url", "")
                r_slug = r_url.rsplit("/", 1)[-1] if r_url else ""
                r_abs = render_inline(ref.get("abstract", []), references).strip()
                out.append(f"- **{r_title}** (`{r_slug}`): {r_abs}")
            out.append("")
    return "\n".join(out).strip() + "\n"


def flatten_index_nodes(nodes: list[dict[str, Any]], parent_section: str = "") -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    section = parent_section
    for node in nodes:
        ntype = node.get("type", "")
        title = (node.get("title") or "").replace("\u2014", " - ")
        path = node.get("path") or ""
        slug = path.rsplit("/", 1)[-1] if path else ""
        if ntype == "groupMarker":
            section = title
            continue
        if path and slug:
            items.append(
                {
                    "title": title,
                    "slug": slug,
                    "path": path,
                    "url": f"https://developer.apple.com{path}",
                    "section": section or title,
                    "type": ntype,
                }
            )
        children = node.get("children", [])
        if children:
            next_section = section or title
            items.extend(flatten_index_nodes(children, next_section))
    return items


def cmd_topic(slug: str) -> int:
    clean_slug = slug.strip().strip("/")
    if clean_slug.startswith("design/human-interface-guidelines/"):
        clean_slug = clean_slug.split("design/human-interface-guidelines/", 1)[1]
    url = f"{TOPIC_BASE_URL}.json" if clean_slug in ("", "human-interface-guidelines") else f"{TOPIC_BASE_URL}/{clean_slug}.json"
    try:
        data = fetch_json(url)
    except urllib.error.HTTPError as exc:
        print(f"Error: HTTP {exc.code} fetching topic '{clean_slug}' from {url}", file=sys.stderr)
        return 1
    print(render_topic_markdown(data, clean_slug or "human-interface-guidelines"))
    return 0


def cmd_search(query: str) -> int:
    index_data = fetch_json(INDEX_URL)
    swift_root = index_data.get("interfaceLanguages", {}).get("swift", [])
    top_children = swift_root[0].get("children", []) if swift_root else []
    all_items = flatten_index_nodes(top_children)
    q = query.lower().strip()
    matches = [
        it
        for it in all_items
        if q in it["title"].lower() or q in it["slug"].lower() or q in it["section"].lower()
    ]
    print(f"Found {len(matches)} Apple HIG topic(s) matching '{query}':\n")
    for m in matches[:50]:
        print(f"- **{m['title']}** (`{m['slug']}`) [{m['section']}] -> {m['url']}")
    return 0


def cmd_sync(output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    index_data = fetch_json(INDEX_URL)
    swift_root = index_data.get("interfaceLanguages", {}).get("swift", [])
    top_children = swift_root[0].get("children", []) if swift_root else []
    all_items = flatten_index_nodes(top_children)

    catalog_lines = [
        "# Apple Human Interface Guidelines - Complete Topic Catalog",
        "",
        f"- **Source**: {WEB_BASE_URL}",
        f"- **Total Topics**: {len(all_items)}",
        "",
        "## Table of Contents",
        "",
    ]
    for pillar in top_children:
        p_title = pillar.get("title", "")
        p_slug = (pillar.get("path") or "").rsplit("/", 1)[-1]
        if p_title and p_slug:
            catalog_lines.append(f"- [{p_title}](#{p_slug}) (`{p_slug}`)")
    catalog_lines.append("")

    for pillar in top_children:
        p_title = pillar.get("title", "")
        p_path = pillar.get("path", "")
        p_slug = p_path.rsplit("/", 1)[-1] if p_path else ""
        if not p_slug:
            continue
        catalog_lines.append(f"## {p_title}")
        catalog_lines.append("")
        pillar_items = flatten_index_nodes(pillar.get("children", []), p_title)
        for item in pillar_items:
            catalog_lines.append(f"- **{item['title']}** (`{item['slug']}`) - {item['url']}")
        catalog_lines.append("")

        try:
            p_data = fetch_json(f"{TOPIC_BASE_URL}/{p_slug}.json")
            p_md = render_topic_markdown(p_data, p_slug)
            (output_dir / f"{p_slug}.md").write_text(p_md, encoding="utf-8")
        except Exception as exc:
            print(f"Warning: could not fetch pillar {p_slug}: {exc}", file=sys.stderr)

    (output_dir / "catalog.md").write_text("\n".join(catalog_lines).strip() + "\n", encoding="utf-8")
    print(f"Success: Synced {len(all_items)} Apple HIG topics into {output_dir}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apple Human Interface Guidelines (HIG) CLI helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_topic = sub.add_parser("topic", help="Fetch and render an Apple HIG topic by slug")
    p_topic.add_argument("slug", help="Topic slug, e.g. color, typography, buttons, designing-for-ios")

    p_search = sub.add_parser("search", help="Search Apple HIG topics by keyword")
    p_search.add_argument("query", help="Search keyword")

    p_sync = sub.add_parser("sync", help="Sync Apple HIG catalog and pillar references")
    default_refs = Path(__file__).resolve().parent.parent / "references"
    p_sync.add_argument("--output-dir", type=Path, default=default_refs, help="Output directory for references")

    args = parser.parse_args(argv)
    if args.cmd == "topic":
        return cmd_topic(args.slug)
    if args.cmd == "search":
        return cmd_search(args.query)
    if args.cmd == "sync":
        return cmd_sync(args.output_dir)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
