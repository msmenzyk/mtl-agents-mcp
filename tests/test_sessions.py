import json

import pytest

from mtl_agents_mcp import sessions

from .conftest import CLAUDE_ID, CODEX_ID


def test_list_sessions_finds_both_tools(stores):
    found = {s.tool: s for s in sessions.list_sessions(days=36500)}
    assert found["claude"].id == CLAUDE_ID
    assert found["claude"].title == "app-tests"  # live name wins over the AI title
    assert found["claude"].running
    assert found["claude"].cwd == "/work/app"
    assert found["codex"].id == CODEX_ID
    assert found["codex"].title == "Review the site"
    assert found["codex"].cwd == "/work/site"


def test_list_sessions_skips_non_uuid_files(stores):
    bad = sessions.CLAUDE_PROJECTS / "-work-app" / "--evil-option.jsonl"
    bad.write_text("{}\n")
    ids = [s.id for s in sessions.list_sessions(days=36500)]
    assert "--evil-option" not in ids


def test_find_session_by_title_and_prefix(stores):
    assert sessions.find_session("review the", days=36500).id == CODEX_ID
    assert sessions.find_session(CLAUDE_ID[:8], days=36500).tool == "claude"
    with pytest.raises(LookupError):
        sessions.find_session("nothing like this", days=36500)


def test_read_messages_keeps_only_text(stores):
    claude = sessions.find_session(CLAUDE_ID, days=36500)
    assert [(m.role, m.text) for m in sessions.read_messages(claude)] == [
        ("user", "How many tests fail?"),
        ("assistant", "Three tests fail."),
    ]
    codex = sessions.find_session(CODEX_ID, days=36500)
    assert [(m.role, m.text) for m in sessions.read_messages(codex)] == [
        ("user", "Review the site"),
        ("assistant", "Found 4 issues."),
    ]


def test_ask_running_claude_writes_inbox(stores):
    claude = sessions.find_session(CLAUDE_ID, days=36500)
    how, replies = sessions.ask(claude, "status?", "Codex [fake] note", wait_seconds=0)
    assert "inbox" in how
    assert replies == []
    (msg_file,) = (sessions.INBOX / CLAUDE_ID).glob("*.json")
    msg = json.loads(msg_file.read_text())
    assert msg["text"] == "status?"
    assert msg["from"] == "Codex fake note"  # brackets stripped from the sender
