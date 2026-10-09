from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards.main_menu import main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    message = (
        f"👋 Welcome {user.first_name}!\n\n"
        "🍽️ Welcome to WKU Catholic Eats!\n\n"
        "Order delicious food from "
        "Catholic Church Restaurant "
        "and get it delivered directly to WKU campus. 🎓🚴\n\n"
        "What would you like to do?"
    )

    await update.message.reply_text(
        message,
        reply_markup=main_menu()
    )