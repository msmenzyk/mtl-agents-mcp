# mtl-agents-mcp

MCP server that lets local Claude Code and Codex sessions see and message each other.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/msmenzyk/mtl-agents-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/msmenzyk/mtl-agents-mcp/actions/workflows/ci.yml)

You run Claude Code in one terminal and Codex in another. Each one only knows its own
session. With this server, any session can ask "what did the Codex review find?" or
"how far is the migration in the other Claude session?" and get an answer.

## Features

- `list_sessions`: recent Claude Code and Codex sessions, with title, folder and whether they are running.
- `read_session`: the last messages of a session (text only, no tool calls). Cheap and read-only.
- `ask_session`: send a question to another session and wait for the answer.

How `ask_session` delivers a message:

| Target | Running | Closed |
|---|---|---|
| Codex | `codex queue` into the live session | `codex exec resume` |
| Claude Code | inbox file, picked up by a hook on its next turn | `claude -p --resume --fork-session` |

An idle Claude Code session only answers after someone types in it. A busy one answers when its current turn ends.

## Quick Start

### Prerequisites

- Python 3.10+ and [Poetry](https://python-poetry.org/)
- Claude Code and/or Codex CLI (`codex queue` needs a recent Codex version)
- `jq` for the hook install script
- macOS or Linux

### Installation

```bash
git clone https://github.com/msmenzyk/mtl-agents-mcp.git
cd mtl-agents-mcp
poetry install
```

Register the server in Claude Code:

```bash
claude mcp add -s user mtl-agents -- bash -c "cd $PWD && poetry run python -m mtl_agents_mcp"
```

Register it in Codex (`~/.codex/config.toml`, use your real path):

```toml
[mcp_servers.mtl-agents]
command = "bash"
args = ["-c", "cd /path/to/mtl-agents-mcp && poetry run python -m mtl_agents_mcp"]
tool_timeout_sec = 300
```

Install the inbox hook, so running Claude Code sessions can receive messages. It adds
itself to `UserPromptSubmit` and `Stop` in `~/.claude/settings.json` and keeps a backup:

```bash
./hooks/install_claude_hook.sh
```

Restart your sessions so they load the new tools.

### Usage

In any Claude Code or Codex session:

```
Use mtl-agents to list my running sessions.
Read the last 5 messages of the Codex session "Review the login flow".
Ask the Claude session in my-api how many tests still fail.
```

## Where it reads from

- Claude Code: `~/.claude/projects/*/*.jsonl`, running sessions from `~/.claude/sessions/<pid>.json`
- Codex: `~/.codex/sessions/**/rollout-*.jsonl`, titles from `~/.codex/session_index.jsonl`.
  A Codex session counts as running when its log changed in the last 15 minutes.
- Inbox for Claude Code: `~/.agents/inbox/<session-id>/`

These are internal formats of both tools and can change between versions. If a tool update
breaks parsing, please open an issue with your versions.

## Development

```bash
git clone https://github.com/msmenzyk/mtl-agents-mcp.git
cd mtl-agents-mcp
poetry install
poetry run pytest
poetry run ruff check . && poetry run ruff format --check .
```

Tests use fake session stores in a temp folder and never touch your real sessions.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a PR.

## Security

This server reads every session transcript of your user, and `ask_session` can start agent
runs in other projects. Read the threat model in [SECURITY.md](SECURITY.md). To report a
vulnerability, see the same file.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">
  MusicTech Lab - Rockstars Developers dedicated to the Music Industry<br>
  <a href="https://musictechlab.io">Website</a>
  <span> | </span>
  <a href="https://linkedin.com/company/musictechlab">LinkedIn</a>
  <span> | </span>
  <a href="https://musictechlab.io/contact">Let's talk</a><br>
  Crafted by <a href="https://musictechlab.io">musictechlab.io</a>
</div>
