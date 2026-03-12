---
name: reminders
description: Manage personal reminders — add, list, complete, or delete. Stored locally in data/reminders.json.
user-invocable: true
---

# Reminders Skill

Local JSON-backed reminder management.

## Usage

```python
from skills.reminders import add_reminder, list_reminders, complete_reminder, delete_reminder

add_reminder("Call dentist", remind_at="2025-03-15T09:00:00")
list_reminders()
complete_reminder(reminder_id=1)
delete_reminder(reminder_id=2)
```

## Arguments

`$ARGUMENTS` — action and details, e.g. `add Call dentist` or `list`

## Data

Stored at `data/reminders.json` — plain JSON, easy to inspect and edit.
