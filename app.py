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
