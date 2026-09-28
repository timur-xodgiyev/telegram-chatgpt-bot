import os
import json
from datetime import datetime, timedelta
from pathlib import Path as FSPath

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

ADMIN_ID = 0  # сюда свой Telegram ID
SUBS_FILE = "subs.json"
DAILY_LIMIT = 50
user_chats = {}
usage = {}

def load_subs():
    try:
        return json.loads(FSPath(SUBS_FILE).read_text())
    except Exception:
        return {}

def save_subs(data):
    FSPath(SUBS_FILE).write_text(json.dumps(data, ensure_ascii=False, indent=2))

def is_active(uid):
    if uid == ADMIN_ID:
        return True
    exp = load_subs().get(str(uid))
    if not exp:
        return False
    try:
        return datetime.strptime(exp, "%Y-%m-%d").date() >= datetime.now().date()
    except Exception:
        return False

async def check_access(update: Update):
    uid = update.effective_user.id if update.effective_user else 0
    if not is_active(uid):
        if update.message:
            await update.message.reply_text("Доступ закрыт. Напиши администратору.")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    await update.message.reply_text("Привет! Я ChatGPT-бот. Напиши сообщение или пришли голосовое.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    await update.message.reply_text(
        "Команды:\n/start — запуск\n/help — помощь\n/new — новый диалог"
    )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
