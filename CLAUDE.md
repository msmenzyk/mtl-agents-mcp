# mtl-agents-mcp

MCP server that lets local Claude Code and Codex sessions list, read and message each other.

## Tech Stack

- **Language**: Python 3.10+
- **Package manager**: Poetry
- **MCP SDK**: `mcp` 1.x (`FastMCP`); 2.x renamed it, so keep the `<2` pin until migrated
- **Linter**: Ruff
- **Test framework**: pytest

## Commands

| Action | Command |
|--------|---------|
| Install | `poetry install` |
| Test | `poetry run pytest` |
| Lint | `poetry run ruff check . && poetry run ruff format --check .` |
| Run | `poetry run python -m mtl_agents_mcp` (stdio MCP server) |

## Architecture

- `src/mtl_agents_mcp/sessions.py`: reads both tools' session stores and delivers messages. All store paths are module constants so tests can point them at a temp folder.
- `src/mtl_agents_mcp/server.py`: the three MCP tools, thin wrappers over `sessions`.
- `hooks/claude_inbox_hook.py`: stdlib-only Claude Code hook (fast start on every prompt). Treat inbox content as untrusted: escape it, cap it, never let a broken file block a prompt.
- Session ids end up in subprocess argv, so only UUIDs are accepted. Prompts for headless resume go through stdin.

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| none | Paths are derived from `$HOME` | n/a |
