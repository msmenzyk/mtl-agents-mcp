#!/usr/bin/env python3
"""Claude Code hook (UserPromptSubmit and Stop): hand inbox messages from other sessions to Claude.

Stdlib only, so it starts fast on every prompt. Delivered messages move to inbox/<id>/done/.
"""

import json
import sys
from pathlib import Path

INBOX = Path.home() / ".agents" / "inbox"


def main() -> None:
    event = json.load(sys.stdin)
    box = INBOX / event.get("session_id", "")
    files = sorted(box.glob("*.json")) if box.is_dir() else []
    if not files:
        return
    done = box / "done"
    done.mkdir(exist_ok=True)
    texts = []
    for f in files:
        msg = json.loads(f.read_text())
        texts.append(f"From {msg['from']} at {msg['ts']}:\n{msg['text']}")
        f.rename(done / f.name)
    body = (
        "Messages from other agent sessions arrived through the mtl-agents inbox. "
        "Answer them briefly in your reply, the sender reads your transcript:\n\n"
        + "\n\n".join(texts)
    )
    if event.get("hook_event_name") == "Stop":
        # Blocking the stop makes Claude answer now instead of on the next user prompt.
        print(json.dumps({"decision": "block", "reason": body}))
    else:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": body,
                    }
                }
            )
        )


if __name__ == "__main__":
    main()
