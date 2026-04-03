"""
from flask import Flask, request, jsonify, abort
from datetime import datetime, timezone
from mentor_agent import get_response_from_agent
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
import os

app = Flask(__name__)

# In-memory job tracker (reset on restart; swap for Redis/DB in production)
JOB_STATUS: dict = {}

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# ══════════════════════════════════════════════════════════════
#  Health check
# ══════════════════════════════════════════════════════════════

@app.get("/")
def health():
    return "Mentor Agent OK", 200

# ══════════════════════════════════════════════════════════════
#  REST  /prompt  (for testing or external triggers)
# ══════════════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your chatbot. How can I help you?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # 👇 use your function here
    try: 
        response = get_response_from_agent(user_text)
    
    except Exception as e:
        response = f"Testing..."

    await update.message.reply_text(response)

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error: {context.error}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(handle_error)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
"""
from datetime import datetime, timezone
from mentor_agent import get_response_from_agent
from telegram import Bot, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import os
import re

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# ══════════════════════════════════════════════════════════════
#  knock.txt parser
# ══════════════════════════════════════════════════════════════

def parse_knock_file(filepath: str = "knock.txt") -> list[dict]:
    """
    Parse knock.txt into a list of job dicts.

    Each job block must be separated by a line containing only '---'.
    Supported keys (case-insensitive):
        name     – unique identifier for the job (optional)
        schedule – 'cron MIN HOUR DOM MON DOW' or 'interval <N>m/h/d'
        prompt   – text to send to the agent
        chat_id  – Telegram chat ID to deliver the response (optional)
    """
    jobs: list[dict] = []

    if not os.path.exists(filepath):
        print(f"[knock] '{filepath}' not found — no scheduled jobs loaded.")
        return jobs

    with open(filepath, "r") as f:
        raw = f.read()

    blocks = [b.strip() for b in raw.split("---") if b.strip()]

    for block_index, block in enumerate(blocks):
        job: dict = {}
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                job[key.strip().lower()] = value.strip()

        if "schedule" not in job or "prompt" not in job:
            print(f"[knock] Block {block_index + 1}: missing 'schedule' or 'prompt' — skipped.")
            continue

        jobs.append(job)

    print(f"[knock] Loaded {len(jobs)} job(s) from '{filepath}'.")
    return jobs


# ══════════════════════════════════════════════════════════════
#  Schedule string → APScheduler trigger
# ══════════════════════════════════════════════════════════════

def build_trigger(schedule_str: str):
    """
    Convert a schedule string into an APScheduler trigger.

    Formats accepted:
        cron <MIN> <HOUR> <DOM> <MON> <DOW>
            e.g. cron 0 9 * * *        → every day at 09:00
                 cron 30 17 * * 1-5    → Mon–Fri at 17:30
                 cron 0 8 1 * *        → 1st of every month at 08:00

        interval <N>m | <N>h | <N>d
            e.g. interval 30m          → every 30 minutes
                 interval 6h           → every 6 hours
                 interval 1d           → every day
    """
    parts = schedule_str.split()
    kind  = parts[0].lower()

    if kind == "cron":
        if len(parts) != 6:
            raise ValueError(
                f"'cron' expects exactly 5 fields (MIN HOUR DOM MON DOW), "
                f"got {len(parts) - 1}: '{schedule_str}'"
            )
        minute, hour, dom, month, dow = parts[1:]
        return CronTrigger(
            minute=minute, hour=hour,
            day=dom, month=month, day_of_week=dow,
        )

    elif kind == "interval":
        if len(parts) != 2:
            raise ValueError(f"'interval' expects exactly one value, e.g. '30m': '{schedule_str}'")
        raw = parts[1].lower()
        m = re.fullmatch(r"(\d+)(m|h|d)", raw)
        if not m:
            raise ValueError(
                f"Interval value must match <N>m / <N>h / <N>d, got: '{raw}'"
            )
        amount = int(m.group(1))
        unit   = m.group(2)
        kwargs = (
            {"minutes": amount} if unit == "m" else
            {"hours":   amount} if unit == "h" else
            {"days":    amount}
        )
        return IntervalTrigger(**kwargs)

    else:
        raise ValueError(
            f"Unknown schedule type '{kind}'. Valid types: 'cron', 'interval'."
        )


# ══════════════════════════════════════════════════════════════
#  Scheduled job runner
# ══════════════════════════════════════════════════════════════

async def run_knock_job(prompt: str, chat_id: str, job_name: str, bot: Bot = None) -> None:
    """Invoke the agent with the given prompt and deliver the response."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"[knock] [{timestamp}] Running '{job_name}' | prompt={prompt!r}")

    try:
        response = get_response_from_agent(prompt)
    except Exception as exc:
        response = f"[Agent error in '{job_name}'] {exc}"
        print(f"[knock] ERROR in '{job_name}': {exc}")

    if chat_id:
        try:
            await bot.send_message(chat_id=int(chat_id), text=response)
        except Exception as exc:
            print(f"[knock] Failed to send Telegram message for '{job_name}': {exc}")
    else:
        print(f"[knock] Response for '{job_name}':\n{response}")


# ══════════════════════════════════════════════════════════════
#  Telegram handlers
# ══════════════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I'm your mentor agent. How can I help you?")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    try:
        response = "hello" #get_response_from_agent(user_text)
        #response = await asyncio.wait_for(
            asyncio.to_thread(get_response_from_agent, user_text),
            timeout=180  # 3 minutes, well above your agent's normal 30 seconds
        )
    except Exception:
        response = "Testing..."
    await update.message.reply_text(response)


async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"[telegram] Update {update} caused error: {context.error}")


# ══════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════

def main() -> None:
    # ── Build scheduler and register jobs from knock.txt ───────
    # Jobs are added now (no event loop needed), but .start() is
    # deferred to post_init which runs inside the running loop.
    scheduler = AsyncIOScheduler()

    for index, job in enumerate(parse_knock_file("knock.txt")):
        job_name = job.get("name", f"knock_job_{index + 1}")
        chat_id  = job.get("chat_id", "")
        prompt   = job["prompt"]

        try:
            trigger = build_trigger(job["schedule"])
            scheduler.add_job(
                run_knock_job,
                trigger=trigger,
                kwargs={
                    "prompt":   prompt,
                    "chat_id":  chat_id,
                    "job_name": job_name,
                },
                id=job_name,
                name=job_name,
                misfire_grace_time=60,
                replace_existing=True,
            )
            print(f"[knock] Registered: '{job_name}' → schedule='{job['schedule']}'")
        except Exception as exc:
            print(f"[knock] Could not register '{job_name}': {exc}")

    # ── post_init runs inside the event loop created by run_polling
    async def post_init(application: Application) -> None:
        # Patch the bot reference into every registered job now that
        # the Application (and its Bot) is fully initialised.
        for job in scheduler.get_jobs():
            updated_kwargs = dict(job.kwargs)
            updated_kwargs["bot"] = application.bot
            job.modify(kwargs=updated_kwargs)
        scheduler.start()
        print("[knock] Scheduler started.")

    # ── Wire up the Telegram application ───────────────────────
    telegram_app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    telegram_app.add_error_handler(handle_error)

    # ── Start polling (creates + runs the event loop) ──────────
    print("[telegram] Bot is running...")
    telegram_app.run_polling()


if __name__ == "__main__":
    main()