# GEMINI.md - apple-design-hig

## Project Overview
`apple-design-hig` maintains the `apple-design-hig` skill and MCP server for Apple's Human Interface Guidelines (`https://developer.apple.com/design/human-interface-guidelines/`).

## Conventions
- Always use `uv` for virtual environment and dependency management (`uv sync`, `uv run pytest`, `uv run apple-design-hig ...`).
- Never use the em dash character in code, documentation, or generated Markdown; use plain hyphens (`-`) instead.
- Keep `skills/apple-design-hig/scripts/hig_fetch.py` compatible with the Python standard library so the packaged skill runs in any environment without external dependencies.
