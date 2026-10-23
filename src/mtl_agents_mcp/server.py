"""MCP server that lets Claude Code and Codex sessions see and message each other."""

import subprocess
from datetime import datetime

from mcp.server.fastmcp import FastMCP

from . import sessions

mcp = FastMCP(
    "mtl-agents",
    instructions=(
        "See and talk to other local Claude Code AND Codex sessions. Prefer these tools over "
        "the built-in ListAgents/SendMessage, which only see Claude sessions. Codex sessions "
        "are named by their first prompt, e.g. 'Sprawdź dostęp do arkusza'. Use list_sessions to find "
        "a session, read_session to see what it has been doing (cheap, read-only), and "
        "ask_session only when you need the session itself to answer. Prefer read_session "
        "when the answer is probably already in its log. Refer to sessions by id or title."
    ),
)


def _fmt_time(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


@mcp.tool()
def list_sessions(
    tool: str = "all", days: float = 3, running_only: bool = False
) -> str:
    """List recent Claude Code and Codex sessions on this machine.

    Args:
        tool: "all", "claude" or "codex".
        days: How far back to look.
        running_only: Only sessions that are open right now.
    """
    found = sessions.list_sessions(tool, days)
    if running_only:
        found = [s for s in found if s.running]
    if not found:
        return "No sessions found."
    lines = [
        "| tool | id | title | cwd | updated | running |",
        "|---|---|---|---|---|---|",
    ]
    for s in found:
        lines.append(
            f"| {s.tool} | {s.id} | {s.title} | {s.cwd} | {_fmt_time(s.updated)} | {'yes' if s.running else ''} |"
        )
    return "\n".join(lines)


@mcp.tool()
def read_session(session: str, last_n: int = 10) -> str:
    """Read the last messages (user and assistant text, no tool calls) of a session.

    Args:
        session: Session id, id prefix, or part of its title.
        last_n: How many messages to return.
    """
    try:
        s = sessions.find_session(session)
    except LookupError as e:
        return str(e)
    msgs = sessions.read_messages(s, last_n)
    header = f"{s.tool} session {s.id} \"{s.title}\" ({'running' if s.running else 'closed'})"
    body = "\n\n".join(f"[{m.ts}] {m.role}: {m.text}" for m in msgs)
    return f"{header}\n\n{body or 'No messages.'}"


@mcp.tool()
def ask_session(
    session: str,
    message: str,
    sender: str = "another agent session",
    wait_seconds: int = 90,
) -> str:
    """Send a question to another session and wait for its answer.

    Running Codex sessions get it through `codex queue`. Running Claude sessions get it from
    an inbox on their next turn (an idle Claude session will not answer until someone types
    in it). Closed sessions are resumed headless; Claude ones are forked so the original
    transcript stays untouched.

    Args:
        session: Session id, id prefix, or part of its title.
        message: The question.
        sender: Who is asking, e.g. "Claude in vimo". Shown to the other session.
        wait_seconds: How long to wait for the answer.
    """
    try:
        s = sessions.find_session(session)
    except LookupError as e:
        return str(e)
    try:
        how, replies = sessions.ask(s, message, sender, wait_seconds)
    except subprocess.CalledProcessError as e:
        return f"Sending failed ({' '.join(e.cmd[:3])}): {e.stderr.strip() or e.stdout.strip()}"
    except subprocess.TimeoutExpired:
        return f"No answer within {wait_seconds}s from the resumed {s.tool} session."
    if not replies:
        return (
            f"Message {how}. No answer within {wait_seconds}s. "
            f"Check later with read_session('{s.id}')."
        )
    answer = "\n\n".join(m.text for m in replies)
    return f'Message {how}. Answer from {s.tool} session "{s.title}":\n\n{answer}'
