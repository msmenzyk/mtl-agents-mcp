# mtl-agents-mcp

MCP server that lets local Claude Code and Codex sessions see and message each other.

## Tools

- `list_sessions`: recent Claude and Codex sessions, with title, folder and whether they are running.
- `read_session`: the last messages of a session (text only, no tool calls). Cheap and read-only.
- `ask_session`: send a question and wait for the answer.

How `ask_session` delivers a message:

| Target | Running | Closed |
|---|---|---|
| Codex | `codex queue` into the live session | `codex exec resume` |
| Claude | inbox file, picked up by a hook on the next turn | `claude -p --resume --fork-session` |

An idle Claude session only answers after someone types in it. A busy one answers when its current turn ends.

## Where it reads from

- Claude: `~/.claude/projects/*/*.jsonl`, live sessions from `~/.claude/sessions/<pid>.json`
- Codex: `~/.codex/sessions/**/rollout-*.jsonl`, titles from `~/.codex/session_index.jsonl`. A Codex session counts as running when its log changed in the last 15 minutes.
- Inbox for Claude: `~/.agents/inbox/<session-id>/`

## Setup

```bash
poetry install
claude mcp add -s user mtl-agents -- bash -c "cd $PWD && poetry run python -m mtl_agents_mcp"
```

Codex, in `~/.codex/config.toml`:

```toml
[mcp_servers.mtl-agents]
command = "bash"
args = ["-c", "cd /Users/msmenzyk/work/mtl/mtl-agents-mcp && poetry run python -m mtl_agents_mcp"]
tool_timeout_sec = 300
```

Claude inbox hook (adds it to `UserPromptSubmit` and `Stop` in `~/.claude/settings.json`, with a backup):

```bash
./hooks/install_claude_hook.sh
```
