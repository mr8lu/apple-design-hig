"""Apple DocC JSON client, Markdown renderer, and skill synchronization helpers."""

from __future__ import annotations

import json
import shutil
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
            "User-Agent": "apple-design-hig/0.1.0 (+https://github.com/mr8lu/apple-design-hig)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize_slug(slug: str) -> str:
    clean = slug.strip().strip("/")
    if clean.startswith("https://developer.apple.com/"):
        clean = clean.split("https://developer.apple.com/", 1)[1].strip("/")
    if clean.startswith("design/human-interface-guidelines"):
        clean = clean[len("design/human-interface-guidelines") :].strip("/")
    return clean


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
            title = (ref.get("title") or ident.rsplit("/", 1)[-1]).replace("\u2014", " - ")
            url = ref.get("url", "")
            if url.startswith("/"):
                url = f"https://developer.apple.com{url}"
            parts.append(f"[{title}]({url})" if url else title)
        elif itype == "image":
            ident = item.get("identifier", "")
            ref = references.get(ident, {})
            alt = (ref.get("alt") or ident).replace("\u2014", " - ")
            parts.append(f"[Image: {alt}]")
        else:
            if "inlineContent" in item:
                parts.append(render_inline(item["inlineContent"], references))
            elif "text" in item:
                parts.append(str(item["text"]).replace("\u2014", " - "))
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
            style = (block.get("name") or block.get("style") or "Note").replace("\u2014", " - ")
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
                title = (ref.get("title") or ident.rsplit("/", 1)[-1]).replace("\u2014", " - ")
                url = ref.get("url", "")
                slug = url.rsplit("/", 1)[-1] if url else ""
                abstract = render_inline(ref.get("abstract", []), references).strip()
                lines.append(f"- **{title}** (`{slug}`): {abstract}")
            lines.append("")
    return lines


def render_topic_markdown(data: dict[str, Any], slug: str) -> str:
    references = data.get("references", {})
    title = (data.get("metadata", {}).get("title") or slug).replace("\u2014", " - ")
    role_heading = (data.get("metadata", {}).get("roleHeading") or "Apple Human Interface Guidelines").replace(
        "\u2014", " - "
    )
    abstract = render_inline(data.get("abstract", []), references).strip()
    canonical_slug = normalize_slug(slug)
    web_url = f"{WEB_BASE_URL}/{canonical_slug}" if canonical_slug else WEB_BASE_URL
    out: list[str] = [
        f"# {title}",
        "",
        f"- **Category**: {role_heading}",
        f"- **Slug**: `{canonical_slug or 'human-interface-guidelines'}`",
        f"- **Official URL**: {web_url}",
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
            t_title = (tsec.get("title") or tsec.get("anchor") or "Subtopics").replace("\u2014", " - ")
            out.append(f"### {t_title}")
            out.append("")
            for ident in tsec.get("identifiers", []):
                ref = references.get(ident, {})
                r_title = (ref.get("title") or ident.rsplit("/", 1)[-1]).replace("\u2014", " - ")
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


def get_index_tree() -> list[dict[str, Any]]:
    index_data = fetch_json(INDEX_URL)
    swift_root = index_data.get("interfaceLanguages", {}).get("swift", [])
    return swift_root[0].get("children", []) if swift_root else []


def list_all_topics() -> list[dict[str, str]]:
    return flatten_index_nodes(get_index_tree())


def search_topics(query: str, section: str | None = None) -> list[dict[str, str]]:
    q = query.lower().strip()
    sec_filter = section.lower().strip() if section else None
    results: list[dict[str, str]] = []
    for item in list_all_topics():
        if sec_filter and sec_filter not in item["section"].lower():
            continue
        if not q or q in item["title"].lower() or q in item["slug"].lower() or q in item["section"].lower():
            results.append(item)
    return results


def get_topic_markdown(slug: str) -> str:
    clean_slug = normalize_slug(slug)
    url = (
        f"{TOPIC_BASE_URL}.json"
        if clean_slug in ("", "human-interface-guidelines")
        else f"{TOPIC_BASE_URL}/{clean_slug}.json"
    )
    data = fetch_json(url)
    return render_topic_markdown(data, clean_slug or "human-interface-guidelines")


def sync_references(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    top_children = get_index_tree()
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

    synced_pillars: list[str] = []
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
            synced_pillars.append(p_slug)
        except urllib.error.URLError:
            pass

    (output_dir / "catalog.md").write_text("\n".join(catalog_lines).strip() + "\n", encoding="utf-8")
    return {
        "total_topics": len(all_items),
        "synced_pillars": synced_pillars,
        "output_dir": str(output_dir),
    }


def install_skill_directories(skill_src_dir: Path, target_roots: list[Path] | None = None) -> list[str]:
    if target_roots is None:
        home = Path.home()
        target_roots = [
            home / ".gemini" / "skills",
            home / ".agents" / "skills",
        ]
    installed: list[str] = []
    for root in target_roots:
        root.mkdir(parents=True, exist_ok=True)
        dest = root / "apple-design-hig"
        if dest.exists() or dest.is_symlink():
            if dest.is_symlink() or dest.is_file():
                dest.unlink()
            else:
                shutil.rmtree(dest)
        shutil.copytree(skill_src_dir, dest)
        installed.append(str(dest))
    return installed
