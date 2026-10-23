#!/usr/bin/env bash
# Adds the inbox hook to UserPromptSubmit and Stop in ~/.claude/settings.json. Safe to run twice.
set -euo pipefail
S="$HOME/.claude/settings.json"
HOOK="python3 $(cd "$(dirname "$0")" && pwd)/claude_inbox_hook.py"
cp "$S" "$S.bak-mtl-agents"
jq --arg c "$HOOK" '
  def add(ev): .hooks[ev] = ((.hooks[ev] // []) as $g
    | if ($g | map(.hooks[]?.command) | index($c)) then $g
      else $g + [{"hooks": [{"type": "command", "command": $c}]}] end);
  add("UserPromptSubmit") | add("Stop")' "$S.bak-mtl-agents" > "$S"
echo "Inbox hook installed. Backup: $S.bak-mtl-agents"
