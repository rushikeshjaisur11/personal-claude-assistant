"""
Claude Code-based orchestrator — no Anthropic API key needed.
Uses the `claude` CLI subprocess with --resume for per-user conversation continuity.
"""

import asyncio
import json
import os

# Project root — run claude from here so it picks up .claude/skills/
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Per-user session IDs for conversation continuity
_sessions: dict[int, str] = {}


async def process_message(user_id: int, text: str) -> str:
    """
    Process a user message via the `claude` CLI and return the response.
    Maintains per-user conversation history through session IDs.
    """
    cmd = ["claude", "--print", "--dangerously-skip-permissions", "--output-format", "json", text]

    session_id = _sessions.get(user_id)
    if session_id:
        cmd = ["claude", "--print", "--dangerously-skip-permissions", "--output-format", "json", "--resume", session_id, text]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=_PROJECT_DIR,
    )
    stdout, stderr = await proc.communicate()

    try:
        data = json.loads(stdout.decode())
        if sid := data.get("session_id"):
            _sessions[user_id] = sid
        return data.get("result", "(no response)").strip()
    except (json.JSONDecodeError, KeyError):
        return stdout.decode().strip() or stderr.decode().strip() or "(no response)"


def clear_history(user_id: int) -> None:
    """Clear conversation history for a user (e.g., /reset command)."""
    _sessions.pop(user_id, None)
