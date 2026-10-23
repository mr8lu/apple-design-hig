"""Unit tests for apple_design_hig."""

from __future__ import annotations

from pathlib import Path

from apple_design_hig.client import (
    flatten_index_nodes,
    install_skill_directories,
    normalize_slug,
    render_topic_markdown,
)


def test_normalize_slug() -> None:
    assert normalize_slug("color") == "color"
    assert normalize_slug("/design/human-interface-guidelines/buttons/") == "buttons"
    assert (
        normalize_slug("https://developer.apple.com/design/human-interface-guidelines/designing-for-ios")
        == "designing-for-ios"
    )


def test_flatten_index_nodes() -> None:
    sample_tree = [
        {
            "title": "Foundations",
            "path": "/design/human-interface-guidelines/foundations",
            "type": "collection",
            "children": [
                {"title": "Visual design", "type": "groupMarker"},
                {
                    "title": "Color",
                    "path": "/design/human-interface-guidelines/color",
                    "type": "article",
                },
                {
                    "title": "Typography",
                    "path": "/design/human-interface-guidelines/typography",
                    "type": "article",
                },
            ],
        }
    ]
    flat = flatten_index_nodes(sample_tree)
    assert len(flat) == 3
    assert flat[0]["slug"] == "foundations"
    assert flat[1]["slug"] == "color"
    assert flat[1]["section"] == "Visual design"
    assert flat[2]["slug"] == "typography"


def test_render_topic_markdown_replaces_em_dash_and_renders_blocks() -> None:
    sample_docc = {
        "metadata": {
            "title": "Color\u2014System Palette",
            "roleHeading": "Foundations",
        },
        "abstract": [{"type": "text", "text": "Use system colors\u2014dynamically adapted for light and dark."}],
        "primaryContentSections": [
            {
                "kind": "content",
                "content": [
                    {"type": "heading", "level": 2, "text": "Best practices"},
                    {
                        "type": "unorderedList",
                        "items": [
                            {
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "inlineContent": [
                                            {"type": "strong", "inlineContent": [{"type": "text", "text": "Ensure contrast."}]},
                                            {"type": "text", "text": " Aim for 7:1 contrast ratio."},
                                        ],
                                    }
                                ]
                            }
                        ],
                    },
                ],
            }
        ],
        "topicSections": [
            {
                "title": "Related",
                "identifiers": ["doc://com.apple.HIG/design/Human-Interface-Guidelines/dark-mode"],
            }
        ],
        "references": {
            "doc://com.apple.HIG/design/Human-Interface-Guidelines/dark-mode": {
                "title": "Dark Mode",
                "url": "/design/human-interface-guidelines/dark-mode",
                "abstract": [{"type": "text", "text": "Support dark environments."}],
            }
        },
    }
    md = render_topic_markdown(sample_docc, "color")
    assert "\u2014" not in md
    assert "# Color - System Palette" in md
    assert "## Best practices" in md
    assert "- **Ensure contrast.** Aim for 7:1 contrast ratio." in md
    assert "- **Dark Mode** (`dark-mode`): Support dark environments." in md


def test_install_skill_directories(tmp_path: Path) -> None:
    src = tmp_path / "src_skill"
    src.mkdir()
    (src / "SKILL.md").write_text("---\nname: apple-design-hig\ndescription: test\n---\n", encoding="utf-8")
    target_a = tmp_path / "target_a"
    target_b = tmp_path / "target_b"
    installed = install_skill_directories(src, [target_a, target_b])
    assert len(installed) == 2
    assert (target_a / "apple-design-hig" / "SKILL.md").is_file()
    assert (target_b / "apple-design-hig" / "SKILL.md").is_file()


def test_no_personal_footprint_in_repo_files() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    checked_paths = [
        repo_root / "README.md",
        repo_root / "GEMINI.md",
        repo_root / "pyproject.toml",
        repo_root / "skills" / "apple-design-hig" / "SKILL.md",
        *repo_root.glob("src/**/*.py"),
        *repo_root.glob("skills/**/*.py"),
        *repo_root.glob("tests/**/*.py"),
    ]
    user_home_prefix = "/" + "Users/"
    linux_home_prefix = "/" + "home/"
    for path in checked_paths:
        content = path.read_text(encoding="utf-8")
        assert user_home_prefix not in content, f"Local macOS path found in {path.relative_to(repo_root)}"
        assert linux_home_prefix not in content, f"Local Linux path found in {path.relative_to(repo_root)}"
        if path.suffix == ".md":
            assert "\u2014" not in content, f"Em-dash found in {path.relative_to(repo_root)}"


