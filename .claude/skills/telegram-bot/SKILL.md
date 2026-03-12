---
name: telegram-bot
description: Start, stop, or manage the personal Claude AI Telegram bot
user-invocable: true
---

# Telegram Bot Skill

Manages the personal Claude AI assistant Telegram bot.

## Start the bot

```bash
cd $ARGUMENTS_OR_PROJECT_ROOT
python main.py
```

## Architecture

```
main.py
  └── telegram_bot.py       ← Telegram message handling (python-telegram-bot)
        └── orchestrator.py ← Claude API tool-use loop + conversation history
              ├── skills/web_search.py     ← DuckDuckGo (no key)
              ├── skills/weather.py        ← Open-Meteo (no key)
              ├── skills/reminders.py      ← JSON-backed local reminders
              ├── skills/summarizer.py     ← URL text extraction
              ├── skills/news.py           ← RSS + HackerNews
              ├── skills/code_executor.py  ← Sandboxed Python runner
              ├── agents/research_agent.py ← Multi-search research subagent
              └── agents/code_agent.py     ← Write-test-fix code subagent
```

## Setup

1. Copy `.env.example` to `.env` and fill in your keys.
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | From @BotFather on Telegram |
| `ANTHROPIC_API_KEY` | Yes | From console.anthropic.com |
| `ALLOWED_USER_IDS` | No | Comma-separated Telegram user IDs (empty = allow all) |
| `CLAUDE_MODEL` | No | Default: `claude-sonnet-4-6` |
