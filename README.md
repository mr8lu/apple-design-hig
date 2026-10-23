# apple-design-hig

Apple Human Interface Guidelines (HIG) agent skill, CLI updater, and Model Context Protocol (MCP) server powered by Apple's official DocC JSON endpoints.

- **Official Apple HIG**: https://developer.apple.com/design/human-interface-guidelines/
- **Skill Name**: `apple-design-hig`
- **Repository**: `https://github.com/mr8lu/apple-design-hig`

## Features

1. **Bundled Agent Skill (`skills/apple-design-hig/`)**:
   - Comprehensive `SKILL.md` covering core design principles, foundations (accessibility, WCAG AA/AAA contrast, color, typography, layout, materials/Liquid Glass), and platform guides (`iOS`, `iPadOS`, `macOS`, `watchOS`, `tvOS`, `visionOS`).
   - Pre-built `references/` catalog of 172+ official Apple HIG topics synced directly from Apple's DocC API.
   - Zero-dependency standalone helper `scripts/hig_fetch.py` for on-demand topic fetching.
2. **CLI Updater (`apple-design-hig`)**:
   - `uv run apple-design-hig sync` - Fetches Apple's live DocC index and updates `skills/apple-design-hig/references/`.
   - `uv run apple-design-hig search <query>` - Searches across all Apple HIG topics by title, slug, or section.
   - `uv run apple-design-hig topic <slug>` - Fetches and renders any Apple HIG article (for example `color`, `typography`, `buttons`, `designing-for-visionos`) into clean Markdown.
   - `uv run apple-design-hig install-skill` - Installs and syncs `apple-design-hig` into `~/.gemini/skills/apple-design-hig` and `~/.agents/skills/apple-design-hig`.
3. **MCP Server (`apple-design-hig-mcp`)**:
   - Exposes `hig_list_sections`, `hig_search`, `hig_get_topic`, and `hig_sync` over stdio for Gemini CLI and MCP-compatible agents.
4. **Automated GitHub Actions Sync (`.github/workflows/sync-hig.yml`)**:
   - Runs weekly (and via `workflow_dispatch`) to pull the latest Apple HIG changes and keep the skill references up to date.

## Quick Start (Prerequisites & Setup)

### Prerequisites
- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) package manager

### Installation & Usage

```bash
cd /path/to/apple-design-hig
uv sync

# Sync latest Apple HIG catalog and pillar references
uv run apple-design-hig sync

# Search topics
uv run apple-design-hig search "navigation"

# Fetch a specific HIG article as Markdown
uv run apple-design-hig topic color

# Install/sync skill into ~/.gemini/skills and ~/.agents/skills
uv run apple-design-hig install-skill

# Run tests
uv run pytest
```

### Registering the MCP Server in Gemini CLI

Add to `~/.gemini/settings.json` under `mcpServers`:

```json
{
  "mcpServers": {
    "apple-design-hig": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/apple-design-hig",
        "run",
        "apple-design-hig-mcp"
      ]
    }
  }
}
```
