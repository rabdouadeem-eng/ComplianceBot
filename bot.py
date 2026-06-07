import os
import asyncio
import logging
import requests
from openai import OpenAI
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ComplianceBot")

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN missing")
if not OPENROUTER_KEY:
    logger.error("❌ OPENROUTER_KEY missing")

client = OpenAI(api_key=OPENROUTER_KEY, base_url="https://openrouter.ai/api/v1")

# النموذج الجديد المجاني والموصى به
MODEL = "amazon/nova-lite-v1:free"

async def start(update, context):
    await update.message.reply_text("👋 Hello! I'm ComplianceBot.\nSend me any business compliance question.")

async def handle_message(update, context):
    user_text = update.message.text
    await update.message.reply_text("⏳ Thinking...")
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": user_text}],
            max_tokens=300,
            temperature=0.7
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"AI error: {e}")
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

def main():
    # حل مشكلة event loop في Python 3.14+
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("✅ ComplianceBot is polling...")
    
    try:
        loop.run_until_complete(app.run_polling())
    finally:
        loop.close()

if __name__ == "__main__":
    main()
