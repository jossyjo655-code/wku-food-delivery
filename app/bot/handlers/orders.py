from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import ContextTypes

from app.bot.handlers.student import FOODS


# =========================================================
# ADD FOOD TO CART
# =========================================================

async def add_food_to_cart(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    await query.answer()

    food_id = int(query.data.split("_")[1])

    food = FOODS.get(food_id)

    if not food:
        await query.answer(
            "Food not found!",
            show_alert=True
        )
        return

    if "cart" not in context.user_data:
        context.user_data["cart"] = []

    context.user_data["cart"].append({
        "food_id": food_id,
        "name": food["name"],
        "price": food["price"],
        "quantity": 1
    })

    keyboard = [
        [
            InlineKeyboardButton(
                "🍔 Continue Shopping",
                callback_data="order_food"
            )
        ],
        [
            InlineKeyboardButton(
                "🛒 View Cart",
                callback_data="view_cart"
            )
        ]
    ]

    await query.edit_message_text(
        f"✅ {food['name']} added to your cart!\n\n"
        f"Price: {food['price']} ETB",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# VIEW CART
# =========================================================

async def view_cart(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    await query.answer()

    cart = context.user_data.get("cart", [])

    # -----------------------------------------------------
    # EMPTY CART
    # -----------------------------------------------------

    if not cart:

        keyboard = [
            [
                InlineKeyboardButton(
                    "🍔 Order Food",
                    callback_data="order_food"
                )
            ]
        ]

        await query.edit_message_text(
            "🛒 YOUR CART\n\n"
            "Your cart is empty.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    # -----------------------------------------------------
    # CALCULATE TOTAL
    # -----------------------------------------------------

    total = 0

    message = "🛒 YOUR CART\n\n"

    for item in cart:

        subtotal = (
            item["price"] *
            item["quantity"]
        )

        total += subtotal

        message += (
            f"🍽️ {item['name']} × "
            f"{item['quantity']}\n"
            f"💰 {subtotal} ETB\n\n"
        )

    message += (
        f"━━━━━━━━━━━━━━━━\n"
        f"💵 Food Total: {total} ETB"
    )

    # -----------------------------------------------------
    # CART BUTTONS
    # -----------------------------------------------------

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Checkout",
                callback_data="checkout"
            )
        ],
        [
            InlineKeyboardButton(
                "🍔 Continue Shopping",
                callback_data="order_food"
            )
        ]
    ]

    # -----------------------------------------------------
    # SHOW CART
    # -----------------------------------------------------

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )