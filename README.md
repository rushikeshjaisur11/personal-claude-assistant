# Personal Claude Assistant

A self-hosted personal AI assistant powered by Claude Code, delivered entirely through Telegram. No web UI needed — your phone is the interface.

Built with a **skills-first architecture**: every capability is a standalone Python skill module, each paired with a Claude Code `SKILL.md` file. Two specialized subagents handle complex multi-step tasks.

---

## Features

| Skill | What it does | API key needed? |
|---|---|---|
| Web Search | DuckDuckGo real-time search | No |
| Weather | Current conditions + 3-day forecast (Open-Meteo) | No |
| Reminders | Add / list / complete / delete (stored locally) | No |
| News | Headlines from BBC, TechCrunch, ScienceDaily, HackerNews | No |
| Summarize URL | Fetch any URL and summarize its content | No |
| Python Executor | Run Python code in a sandboxed subprocess | No |
| Research Agent | Multi-step subagent: search → synthesize → report | No |
| Code Agent | Subagent: write → execute → debug loop | No |

All features are invoked naturally through conversation — Claude decides which skill(s) to use.

---

## Architecture

```
Telegram (your phone)
        │
        ▼
telegram_bot.py          ← python-telegram-bot v21, handles commands + messages
        │
        ▼
orchestrator.py          ← spawns `claude` CLI subprocess, per-user session history
        │
        └── claude CLI   ← runs in project root, loads .claude/skills/ automatically

.claude/skills/*/SKILL.md            Claude Code skill definitions (weather, news, etc.)
data/reminders.json                  Persistent reminder storage
```

The orchestrator calls `claude --print --output-format json` as a subprocess with `cwd` set to the project root. This means Claude Code picks up all `.claude/skills/` definitions automatically — no separate tool wiring needed.

Claude maintains **per-user conversation history** via session IDs (`--resume`), so you can ask follow-up questions naturally.

---

## Prerequisites

- Python 3.11+
- A Telegram bot token (free, from [@BotFather](https://t.me/BotFather))
- [Claude Code](https://claude.ai/code) installed and authenticated (`claude auth login`)

---

## Setup

### 1. Clone / download the project

```bash
cd personal-claude-assistant
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Authenticate Claude Code

```bash
claude auth login
```

### 4. Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Optional: restrict access to specific Telegram user IDs
# Find your ID by messaging @userinfobot on Telegram
ALLOWED_USER_IDS=123456789
```

### 5. Create your Telegram bot

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the token into your `.env` as `TELEGRAM_BOT_TOKEN`

### 6. Start the bot

```bash
uv run python main.py
```

The bot uses **long polling** — no domain, no webhook, no server setup needed. Just run the script and it works.

---

## Usage

Send any message to your bot on Telegram. Claude picks the right skill automatically.

### Example conversations

```
You: What's the weather in Tokyo?
Bot: 🌤 Tokyo, Japan — 18°C, feels like 16°C...

You: Search for the latest news on Claude AI
Bot: Here are the top results...

You: Remind me to review the report tomorrow at 9am
Bot: ✅ Reminder added: "Review the report" for 2025-03-13T09:00:00

You: Show my reminders
Bot: 📝 Active reminders:
     #1 — Review the report (due: 2025-03-13T09:00:00)

You: Research how transformer attention mechanisms work
Bot: [Spawns research subagent, performs multiple searches, returns a structured report]

You: Write a Python script that downloads and parses a sitemap XML
Bot: [Spawns code subagent, writes code, tests it, fixes errors, returns working code]

You: Summarize https://en.wikipedia.org/wiki/Large_language_model
Bot: [Fetches URL, extracts text, returns a summary]

You: What are the top HackerNews stories today?
Bot: [Returns top 5 HackerNews stories with links and scores]
```

### Bot commands

| Command | Action |
|---|---|
| `/start` | Introduction and capabilities list |
| `/reset` | Clear conversation history (fresh start) |
| `/help` | Usage tips |

---

## Claude Code Skills

Each skill has a corresponding `SKILL.md` in `.claude/skills/` — used both by the Telegram bot (via the `claude` CLI subprocess) and directly within Claude Code sessions:

| Skill | Invoke with |
|---|---|
| Telegram bot management | `/telegram-bot` |
| Web search | `/web-search <query>` |
| Weather | `/weather <city>` |
| Reminders | `/reminders` |
| URL summarization | `/summarize <url>` |
| News | `/news <topic>` |
| Research subagent | `/research <topic>` |
| Code subagent | `/code-help <task>` |

---

## Project Structure

```
personal-claude-assistant/
├── main.py                        Entry point
├── telegram_bot.py                Telegram handler (commands + messages)
├── orchestrator.py                Claude CLI subprocess wrapper
├── config.py                      Environment config
├── pyproject.toml                 Python dependencies (uv)
├── .env.example                   Environment variable template
│
├── skills/
│   ├── web_search.py              DuckDuckGo search
│   ├── weather.py                 Open-Meteo weather
│   ├── reminders.py               JSON reminder storage
│   ├── summarizer.py              URL content extraction
│   ├── news.py                    RSS + HackerNews feeds
│   └── code_executor.py           Sandboxed Python runner
│
├── agents/
│   ├── research_agent.py          Multi-search research subagent
│   └── code_agent.py              Write-test-fix coding subagent
│
├── data/
│   └── reminders.json             Created automatically on first reminder
│
└── .claude/skills/
    ├── telegram-bot/SKILL.md
    ├── web-search/SKILL.md
    ├── weather/SKILL.md
    ├── reminders/SKILL.md
    ├── summarize/SKILL.md
    ├── news/SKILL.md
    ├── research/SKILL.md
    └── code-help/SKILL.md
```

---

## Configuration Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | — | From @BotFather |
| `ALLOWED_USER_IDS` | No | (all) | Comma-separated Telegram user IDs |

---

## Adding New Skills

1. Create `skills/your_skill.py` with a plain Python function.
2. Create `.claude/skills/your-skill/SKILL.md` describing the skill for Claude Code.

That's it — because the orchestrator runs `claude` from the project root, any new skill defined in `.claude/skills/` is automatically available to the bot.

---

## Security Notes

- Set `ALLOWED_USER_IDS` to restrict the bot to yourself only.
- The Python code executor runs in a subprocess with a 15-second timeout. It is not fully sandboxed — only expose it to trusted users.
- No API keys are stored or logged beyond the Telegram bot token.
- Conversation history is stored in-memory only and reset on bot restart.

---

## License

MIT
