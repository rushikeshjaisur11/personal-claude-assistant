"""
Telegram Bot Handler
Receives messages from Telegram, routes them through the orchestrator,
and sends Claude's response back. No UI needed — Telegram is the interface.
"""

import logging
from datetime import datetime

from telegram import BotCommand, Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import ALLOWED_USER_IDS, TELEGRAM_BOT_TOKEN
from orchestrator import clear_history, process_message
from skills.reminders import complete_reminder, list_reminders

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# Track chat IDs of users who've interacted (for reminder delivery)
_active_chat_ids: set[int] = set(ALLOWED_USER_IDS)

# ── Auth guard ────────────────────────────────────────────────────────────────

def _is_allowed(user_id: int) -> bool:
    if not ALLOWED_USER_IDS:
        return True  # Open to everyone if no allowlist configured
    return user_id in ALLOWED_USER_IDS


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _send_long(update: Update, text: str) -> None:
    """Split messages exceeding Telegram's 4096-char limit."""
    chunk_size = 4096
    for i in range(0, len(text), chunk_size):
        chunk = text[i : i + chunk_size]
        try:
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            # Fallback to plain text if Markdown parse fails
            await update.message.reply_text(chunk)


# ── Command handlers ──────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update.effective_user.id):
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    await update.message.reply_text(
        "👋 *Personal Claude Assistant*\n\n"
        "I'm your AI assistant powered by Claude. Just send me a message!\n\n"
        "*Skills available:*\n"
        "🔍 Web search\n"
        "🌤 Weather (any city)\n"
        "📝 Reminders (add / list / done)\n"
        "📰 News (general / tech / science / business / hackernews)\n"
        "🔗 Summarize any URL\n"
        "🐍 Run Python code\n"
        "🔬 Deep research (multi-agent)\n"
        "💻 Code writing & debugging (subagent)\n\n"
        "Commands: /reset to clear history, /help for tips.",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update.effective_user.id):
        return
    clear_history(update.effective_user.id)
    await update.message.reply_text("✅ Conversation history cleared. Fresh start!")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update.effective_user.id):
        return
    await update.message.reply_text(
        "*Tips:*\n"
        "• Ask anything naturally — I'll pick the right skill.\n"
        "• 'Research X' → spawns a deep research subagent.\n"
        "• 'Write a Python script that...' → spawns a code subagent.\n"
        "• 'Remind me to...' → adds a reminder.\n"
        "• 'Summarize https://...' → fetches and summarizes a URL.\n"
        "• /reset → clears conversation history.\n\n"
        "I maintain context across messages in a session.",
        parse_mode=ParseMode.MARKDOWN,
    )


# ── Main message handler ──────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _is_allowed(user.id):
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    _active_chat_ids.add(user.id)
    user_text = update.message.text
    log.info("User %s (%d): %s", user.username or user.first_name, user.id, user_text[:80])

    # Show typing indicator while processing
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING,
    )

    try:
        reply = await process_message(user.id, user_text)
        await _send_long(update, reply)
    except Exception as exc:
        log.exception("Error processing message for user %d", user.id)
        await update.message.reply_text(f"⚠️ Error: {exc}")


# ── Reminder notification job ─────────────────────────────────────────────────

async def _check_reminders(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fire due reminders and mark them done."""
    if not _active_chat_ids:
        return
    now = datetime.now()
    for reminder in list_reminders():
        remind_at = reminder.get("remind_at")
        if not remind_at:
            continue
        try:
            due = datetime.fromisoformat(remind_at)
            # Strip timezone info to compare in local time
            if due.tzinfo is not None:
                due = due.replace(tzinfo=None)
        except ValueError:
            continue
        if due <= now:
            complete_reminder(reminder["id"])
            text = f"⏰ *Reminder:* {reminder['message']}"
            for chat_id in _active_chat_ids:
                try:
                    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN)
                except Exception:
                    log.exception("Failed to send reminder to chat %d", chat_id)


# ── Bot startup ───────────────────────────────────────────────────────────────

async def _post_init(app: Application) -> None:
    await app.bot.set_my_commands([
        BotCommand("start", "Introduction and capabilities"),
        BotCommand("reset", "Clear conversation history"),
        BotCommand("help", "Usage tips"),
    ])


def run() -> None:
    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(_post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Check for due reminders every 60 seconds
    app.job_queue.run_repeating(_check_reminders, interval=60, first=10)

    log.info("Bot started. Polling for messages...")
    app.run_polling(drop_pending_updates=True)
