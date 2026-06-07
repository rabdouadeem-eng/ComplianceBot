import os
import logging
import asyncio
import requests
from openai import OpenAI
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ComplianceBot")

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

if not BOT_TOKEN or not OPENROUTER_KEY:
    logger.error("❌ Missing environment variables")
    exit(1)

requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True")

client = OpenAI(api_key=OPENROUTER_KEY, base_url="https://openrouter.ai/api/v1")
MODEL = "mistralai/mistral-7b-instruct:free"

async def start(update, context):
    await update.message.reply_text("👋 Hello! I'm ComplianceBot.\nAsk me anything about business compliance.")

async def handle_message(update, context):
    await update.message.reply_text("⏳ Thinking...")
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": update.message.text}],
            max_tokens=300,
            temperature=0.7
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"AI error: {e}")
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

def main():
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("✅ Starting polling...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
