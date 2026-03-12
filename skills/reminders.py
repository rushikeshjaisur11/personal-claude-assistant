"""Skill: Reminders — persistent JSON-backed storage."""

import json
import os
from datetime import datetime

from config import DATA_DIR

REMINDERS_FILE = os.path.join(DATA_DIR, "reminders.json")


def _load() -> list[dict]:
    if not os.path.exists(REMINDERS_FILE):
        return []
    with open(REMINDERS_FILE) as f:
        return json.load(f)


def _save(reminders: list[dict]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders, f, indent=2)


def add_reminder(message: str, remind_at: str | None = None) -> dict:
    """Add a new reminder. remind_at is an optional ISO datetime string."""
    reminders = _load()
    new_id = max((r["id"] for r in reminders), default=0) + 1
    reminder = {
        "id": new_id,
        "message": message,
        "remind_at": remind_at,
        "created_at": datetime.now().isoformat(),
        "done": False,
    }
    reminders.append(reminder)
    _save(reminders)
    return reminder


def list_reminders(include_done: bool = False) -> list[dict]:
    """List active reminders."""
    reminders = _load()
    if not include_done:
        reminders = [r for r in reminders if not r["done"]]
    return reminders


def complete_reminder(reminder_id: int) -> dict:
    """Mark a reminder as done."""
    reminders = _load()
    for r in reminders:
        if r["id"] == reminder_id:
            r["done"] = True
            _save(reminders)
            return {"success": True, "reminder": r}
    return {"success": False, "error": f"Reminder #{reminder_id} not found."}


def delete_reminder(reminder_id: int) -> dict:
    """Permanently delete a reminder."""
    reminders = _load()
    before = len(reminders)
    reminders = [r for r in reminders if r["id"] != reminder_id]
    if len(reminders) == before:
        return {"success": False, "error": f"Reminder #{reminder_id} not found."}
    _save(reminders)
    return {"success": True}
