import json
import os

import pytest

from mtl_agents_mcp import sessions

CLAUDE_ID = "11111111-1111-4111-8111-111111111111"
CODEX_ID = "22222222-2222-4222-8222-222222222222"


def _write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


@pytest.fixture
def stores(tmp_path, monkeypatch):
    """Fake ~/.claude and ~/.codex stores with one session each."""
    claude_projects = tmp_path / "claude" / "projects"
    claude_live = tmp_path / "claude" / "sessions"
    codex_sessions = tmp_path / "codex" / "sessions"
    codex_index = tmp_path / "codex" / "session_index.jsonl"
    claude_live.mkdir(parents=True)

    _write_jsonl(
        claude_projects / "-work-app" / f"{CLAUDE_ID}.jsonl",
        [
            {
                "type": "user",
                "cwd": "/work/app",
                "timestamp": "2026-01-01T10:00:00.000Z",
                "message": {"content": "How many tests fail?"},
            },
            {"type": "user", "isMeta": True, "message": {"content": "hidden"}},
            {
                "type": "assistant",
                "timestamp": "2026-01-01T10:00:05.000Z",
                "message": {"content": [{"type": "thinking", "thinking": "x"}]},
            },
            {
                "type": "assistant",
                "timestamp": "2026-01-01T10:00:06.000Z",
                "message": {"content": [{"type": "text", "text": "Three tests fail."}]},
            },
            {"type": "ai-title", "aiTitle": "Fix failing tests"},
        ],
    )
    # This test process stands in for the live Claude session.
    (claude_live / "1.json").write_text(
        json.dumps({"pid": os.getpid(), "sessionId": CLAUDE_ID, "name": "app-tests"})
    )

    _write_jsonl(
        codex_sessions
        / "2026"
        / "01"
        / "01"
        / f"rollout-2026-01-01T09-00-00-{CODEX_ID}.jsonl",
        [
            {"type": "session_meta", "payload": {"id": CODEX_ID, "cwd": "/work/site"}},
            {
                "type": "response_item",
                "timestamp": "2026-01-01T09:00:01.000Z",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "<environment_context>"}
                    ],
                },
            },
            {
                "type": "response_item",
                "timestamp": "2026-01-01T09:00:02.000Z",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Review the site"}],
                },
            },
            {
                "type": "response_item",
                "timestamp": "2026-01-01T09:00:03.000Z",
                "payload": {"type": "function_call", "name": "shell"},
            },
            {
                "type": "response_item",
                "timestamp": "2026-01-01T09:00:09.000Z",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "Found 4 issues."}],
                },
            },
        ],
    )
    _write_jsonl(codex_index, [{"id": CODEX_ID, "thread_name": "Review the site"}])

    monkeypatch.setattr(sessions, "CLAUDE_PROJECTS", claude_projects)
    monkeypatch.setattr(sessions, "CLAUDE_LIVE", claude_live)
    monkeypatch.setattr(sessions, "CODEX_SESSIONS", codex_sessions)
    monkeypatch.setattr(sessions, "CODEX_INDEX", codex_index)
    monkeypatch.setattr(sessions, "INBOX", tmp_path / "inbox")
    return tmp_path
