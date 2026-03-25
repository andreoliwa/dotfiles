#!/usr/bin/env python3
"""Track per-prompt elapsed time and accumulate session total.

Usage: ``prompt-timer.py start | stop``.

State is stored in /tmp/claude_timer_<ppid>.json, scoped to the parent process PID.

Configure in ~/.claude/settings.json:

    "hooks": {
        "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "~/.claude/hooks/prompt-timer.py start"}]}],
        "Stop":             [{"hooks": [{"type": "command", "command": "~/.claude/hooks/prompt-timer.py stop"}]}]
    }

The Stop hook returns a JSON systemMessage with per-prompt and cumulative session
elapsed times, which Claude Code displays in the conversation.
"""

import json
import os
import sys
import time
from pathlib import Path

_SECS_PER_MINUTE = 60
STATE_FILE = Path(f"/tmp/claude_timer_{os.getppid()}.json")  # noqa: S108


def load_state() -> dict:
    """Load timer state from disk, returning defaults if missing or corrupt."""
    try:
        return json.loads(STATE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"total_ms": 0}


def save_state(state: dict) -> None:
    """Persist timer state to disk."""
    STATE_FILE.write_text(json.dumps(state))


def format_duration(ms: int) -> str:
    """Format milliseconds as a human-readable duration string."""
    secs = ms // 1000
    millis = ms % 1000
    if secs >= _SECS_PER_MINUTE:
        return f"{secs // _SECS_PER_MINUTE}m {secs % _SECS_PER_MINUTE}.{millis:03d}s"
    return f"{secs}.{millis:03d}s"


def now_ms() -> int:
    """Return the current time in milliseconds."""
    return int(time.time() * 1000)


match sys.argv[1] if len(sys.argv) > 1 else "":
    case "start":
        state = load_state()
        state["prompt_start"] = now_ms()
        save_state(state)

    case "stop":
        state = load_state()
        if "prompt_start" not in state:
            print("{}")
            sys.exit(0)

        elapsed = now_ms() - state.pop("prompt_start")
        state["total_ms"] = state.get("total_ms", 0) + elapsed
        save_state(state)

        timestamp = time.strftime("%H:%M:%S")
        print(
            json.dumps(
                {
                    "systemMessage": (
                        f"{timestamp} — "
                        f"elapsed: {format_duration(elapsed)}, "
                        f"session total: {format_duration(state['total_ms'])}"
                    )
                }
            )
        )

    case _:
        print(f"Usage: {sys.argv[0]} start|stop", file=sys.stderr)
        sys.exit(1)
