from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# ⚠️ Сюда вставь свой токен от @BotFather
BOT_TOKEN = "8707623214:AAFUC94RABUQ0nkGsWx8ttNoEx28ZBjPiwo"

# После деплоя на Vercel — замени на свой URL
WEBAPP_URL = "https://djlgbvduaqmwwirwvvjz.supabase.co"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "друг"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "🎓 Открыть Donish AI",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])

    await update.message.reply_text(
        f"Салом, {name}! 👋\n\n"
        f"Мен *Donish AI* — сенинг AI-репетиторинг!\n\n"
        f"📚 Математика, Физика, Английский\n"
        f"💻 IT, Python, Docker, Git\n"
        f"🤖 Искусственный интеллект и CV\n"
        f"📸 Фото → Решение\n\n"
        f"🇷🇺 Русский | 🇹🇯 Тоҷикӣ\n\n"
        f"Нажми кнопку ниже чтобы начать! 👇",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 Помощь Donish AI:\n\n"
        "/start — Открыть приложение\n"
        "/help — Эта справка\n\n"
        "Просто нажми кнопку в /start и учись!"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    print("🚀 Donish AI Bot запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()