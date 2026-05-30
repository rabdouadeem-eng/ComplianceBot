import os
import requests
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, 
    MessageHandler, filters, ContextTypes
)
from dotenv import load_dotenv

# تحميل المتغيرات
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = """أنت ComplianceBot، مستشار ذكي 
للشركات الصغيرة. تساعد في أسئلة 
الامتثال التجاري بالعربية. ردود 
قصيرة ومفيدة. لا تعطي رأياً 
قانونياً رسمياً."""

def ask_kimi(user_message: str) -> str:
    """إرسال السؤال لـ Kimi عبر OpenRouter"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "moonshotai/kimi-k2:free",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    }
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers, json=data, timeout=30
        )
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ خطأ في الاتصال: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب"""
    await update.message.reply_text(
        "👋 مرحباً! أنا ComplianceBot\n"
        "مستشارك الذكي للامتثال التجاري\n\n"
        "اسألني أي سؤال عن:\n"
        "• السجل التجاري\n"
        "• الضرائب والرسوم\n"
        "• العقود والتراخيص\n\n"
        "اكتب /help للمزيد"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شرح الخدمات"""
    await update.message.reply_text(
        "📋 خدمات ComplianceBot:\n\n"
        "✅ أسئلة الامتثال التجاري\n"
        "✅ متطلبات التراخيص\n"
        "✅ الالتزامات الضريبية\n"
        "✅ إرشادات العقود\n\n"
        "⚠️ للقرارات الرسمية راجع مختصاً"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة رسائل المستخدم"""
    await update.message.reply_text("⏳ جاري المعالجة...")
    reply = ask_kimi(update.message.text)
    await update.message.reply_text(reply)

def main():
    """تشغيل البوت"""
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message
    ))
    print("✅ ComplianceBot يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()
