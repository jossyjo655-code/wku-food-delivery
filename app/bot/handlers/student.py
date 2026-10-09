from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


FOODS = {
    1: {
        "name": "🍗 Chicken",
        "price": 200
    },

    2: {
        "name": "🍚 Rice",
        "price": 200
    },

    3: {
        "name": "🍝 Pasta",
        "price": 200
    },

    4: {
        "name": "🥘 Traditional Food",
        "price": 200
    }
}


async def show_food_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    keyboard = []

    for food_id, food in FOODS.items():

        button = InlineKeyboardButton(
            f"{food['name']} - {food['price']} ETB",
            callback_data=f"food_{food_id}"
        )

        keyboard.append([button])

    keyboard.append([
        InlineKeyboardButton(
            "🛒 View Cart",
            callback_data="view_cart"
        )
    ])

    await query.edit_message_text(
        "🍽️ CATHOLIC CHURCH FOOD MENU\n\n"
        "Choose the food you want:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )