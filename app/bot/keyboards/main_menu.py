from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                "🍔 Order Food",
                callback_data="order_food"
            )
        ],
        [
            InlineKeyboardButton(
                "📦 My Orders",
                callback_data="my_orders"
            ),
            InlineKeyboardButton(
                "👤 My Profile",
                callback_data="profile"
            )
        ],
        [
            InlineKeyboardButton(
                "ℹ️ Help",
                callback_data="help"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)