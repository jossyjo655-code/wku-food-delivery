from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.config import BOT_TOKEN

from app.bot.handlers.start import start
from app.bot.handlers.student import show_food_menu
from app.bot.handlers.orders import add_food_to_cart, view_cart

from app.bot.handlers.checkout import (
    start_checkout,
    receive_phone,
    select_location,
    receive_custom_location,
    confirm_order,
    cancel_checkout,
    cancel_command,
)

from app.bot.states import PHONE, LOCATION, CONFIRM


# =========================================================
# GENERAL BUTTON HANDLER
# =========================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    if not query:
        return

    await query.answer()

    if query.data == "order_food":

        await show_food_menu(
            update,
            context
        )

    elif query.data.startswith("food_"):

        await add_food_to_cart(
            update,
            context
        )

    elif query.data == "view_cart":

        await view_cart(
            update,
            context
        )

    elif query.data == "my_orders":

        await query.edit_message_text(
            "📦 MY ORDERS\n\n"
            "You don't have any orders yet."
        )

    elif query.data == "profile":

        user = update.effective_user

        await query.edit_message_text(
            "👤 YOUR PROFILE\n\n"
            f"Name: {user.first_name}\n"
            f"Username: @{user.username or 'Not set'}"
        )

    elif query.data == "help":

        await query.edit_message_text(
            "ℹ️ HELP\n\n"
            "1️⃣ Choose Order Food\n"
            "2️⃣ Select your food\n"
            "3️⃣ Add food to cart\n"
            "4️⃣ Checkout\n"
            "5️⃣ Enter your phone number\n"
            "6️⃣ Select delivery location\n"
            "7️⃣ Confirm your order\n\n"
            "🚴 Your food will be delivered directly "
            "to your selected WKU campus location."
        )


# =========================================================
# MAIN
# =========================================================

def main():

    print("🚀 Starting WKU Catholic Eats...")

    application = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    # =====================================================
    # CHECKOUT CONVERSATION
    # =====================================================

    checkout_conversation = ConversationHandler(

        entry_points=[
            CallbackQueryHandler(
                start_checkout,
                pattern=r"^checkout$"
            )
        ],

        states={

            # ---------------------------------------------
            # PHONE
            # ---------------------------------------------

            PHONE: [

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_phone
                )

            ],

            # ---------------------------------------------
            # LOCATION
            # ---------------------------------------------

           LOCATION: [
    CallbackQueryHandler(
        select_location,
        pattern=r"^loc_(grill_parking|boy_parking|central_library|other)$"
    ),

    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        receive_custom_location
    )
],

            # ---------------------------------------------
            # CONFIRM
            # ---------------------------------------------

            CONFIRM: [

                CallbackQueryHandler(
                    confirm_order,
                    pattern=r"^confirm_order$"
                ),

                CallbackQueryHandler(
                    cancel_checkout,
                    pattern=r"^cancel_checkout$"
                )

            ]

        },

        fallbacks=[

            CommandHandler(
                "cancel",
                cancel_command
            )

        ],

        allow_reentry=True,

        per_message=False
    )

    # =====================================================
    # IMPORTANT:
    # CHECKOUT CONVERSATION MUST BE ADDED FIRST
    # =====================================================

    application.add_handler(
        checkout_conversation
    )

    # =====================================================
    # START COMMAND
    # =====================================================

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # =====================================================
    # GENERAL BUTTONS
    #
    # IMPORTANT:
    # DO NOT INCLUDE checkout,
    # confirm_order, cancel_checkout,
    # OR loc_* HERE.
    # =====================================================

    application.add_handler(
        CallbackQueryHandler(
            button_handler,
            pattern=r"^(order_food|food_.*|view_cart|my_orders|profile|help)$"
        )
    )

    print("✅ Bot is running...")
    print("📱 Students can enter phone numbers manually.")

    application.run_polling()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()