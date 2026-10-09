from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from app.bot.states import PHONE, LOCATION, CONFIRM
from app.database.connection import get_connection


# =========================================================
# START CHECKOUT
# =========================================================

async def start_checkout(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    print("🔥🔥🔥 CHECKOUT HANDLER CALLED 🔥🔥🔥")

    query = update.callback_query
    await query.answer()

    cart = context.user_data.get("cart", [])

    if not cart:
        await query.edit_message_text(
            "🛒 Your cart is empty.\n\n"
            "Please add food to your cart before checkout."
        )

        return ConversationHandler.END

    await query.edit_message_text(
        "🛒 CHECKOUT\n\n"
        "📱 Please enter your phone number manually.\n\n"
        "Example:\n"
        "0912345678\n\n"
        "You can also enter:\n"
        "+251912345678\n\n"
        "Type /cancel to cancel checkout."
    )

    return PHONE


# =========================================================
# RECEIVE PHONE NUMBER
# =========================================================

async def receive_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message or not update.message.text:
        return PHONE

    phone = update.message.text.strip()

    phone = (
        phone
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    valid_phone = False

    # 0912345678
    if phone.startswith("09"):

        if len(phone) == 10 and phone.isdigit():
            valid_phone = True

    # +251912345678
    elif phone.startswith("+2519"):

        if len(phone) == 13 and phone[1:].isdigit():
            valid_phone = True

    # 251912345678
    elif phone.startswith("2519"):

        if len(phone) == 12 and phone.isdigit():
            valid_phone = True

    if not valid_phone:

        await update.message.reply_text(
            "❌ Invalid phone number.\n\n"
            "Please enter a valid Ethiopian phone number.\n\n"
            "Examples:\n"
            "0912345678\n"
            "+251912345678\n"
            "251912345678"
        )

        return PHONE

    context.user_data["phone"] = phone

    keyboard = [
        [
            InlineKeyboardButton(
                "🔥 Grill Parking",
                callback_data="loc_grill_parking"
            )
        ],
        [
            InlineKeyboardButton(
                "🚗 Boy Parking",
                callback_data="loc_boy_parking"
            )
        ],
        [
            InlineKeyboardButton(
                "📚 Central Library",
                callback_data="loc_central_library"
            )
        ],
        [
            InlineKeyboardButton(
                "📍 Other Location",
                callback_data="loc_other"
            )
        ]
    ]

    await update.message.reply_text(
        "✅ Phone number saved!\n\n"
        "📍 WHERE SHOULD WE DELIVER?\n\n"
        "Choose the place where you want to receive your food.",
        reply_markup=ReplyKeyboardRemove()
    )

    await update.message.reply_text(
        "📍 Select your WKU delivery location:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return LOCATION


# =========================================================
# SELECT DELIVERY LOCATION
# =========================================================

async def select_location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    print("📍 LOCATION BUTTON CLICKED:", query.data)

    locations = {
        "loc_grill_parking": "Grill Parking",
        "loc_boy_parking": "Boy Parking",
        "loc_central_library": "Central Library"
    }

    # -----------------------------------------------------
    # OTHER LOCATION
    # -----------------------------------------------------

    if query.data == "loc_other":

        await query.edit_message_text(
            "📍 OTHER DELIVERY LOCATION\n\n"
            "Please type the location where you want "
            "your food delivered.\n\n"
            "Example:\n"
            "Near Main Gate\n"
            "or\n"
            "Student Dorm Block A"
        )

        return LOCATION

    # -----------------------------------------------------
    # GET SELECTED LOCATION
    # -----------------------------------------------------

    location = locations.get(query.data)

    if not location:

        await query.edit_message_text(
            "❌ Location not found.\n\n"
            "Please choose a location again."
        )

        return LOCATION

    context.user_data["delivery_location"] = location

    print("✅ Selected location:", location)

    await show_order_summary(
        update,
        context
    )

    return CONFIRM


# =========================================================
# RECEIVE CUSTOM LOCATION
# =========================================================

async def receive_custom_location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message or not update.message.text:

        if update.message:

            await update.message.reply_text(
                "❌ Please type your delivery location."
            )

        return LOCATION

    location = update.message.text.strip()

    if not location:

        await update.message.reply_text(
            "❌ Location cannot be empty.\n\n"
            "Please type your delivery location."
        )

        return LOCATION

    context.user_data["delivery_location"] = location

    print("✅ Custom location:", location)

    await show_order_summary_from_message(
        update,
        context
    )

    return CONFIRM


# =========================================================
# ORDER SUMMARY
# =========================================================

async def show_order_summary(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    cart = context.user_data.get(
        "cart",
        []
    )

    if not cart:

        await query.edit_message_text(
            "❌ Your cart is empty."
        )

        return

    food_total = sum(
        item["price"] * item["quantity"]
        for item in cart
    )

    delivery_fee = 0

    total = food_total + delivery_fee

    location = context.user_data.get(
        "delivery_location",
        "Not selected"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Confirm Order",
                callback_data="confirm_order"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="cancel_checkout"
            )
        ]
    ]

    await query.edit_message_text(
        "🧾 ORDER SUMMARY\n\n"
        f"📍 Delivery Location: {location}\n"
        f"🍽️ Food Total: {food_total} ETB\n"
        f"🚴 Delivery Fee: {delivery_fee} ETB\n"
        f"💰 Total: {total} ETB\n\n"
        "💵 Payment Method: CASH ON DELIVERY\n\n"
        "Please check your order and confirm.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# ORDER SUMMARY FOR CUSTOM LOCATION
# =========================================================

async def show_order_summary_from_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    cart = context.user_data.get(
        "cart",
        []
    )

    if not cart:

        await update.message.reply_text(
            "❌ Your cart is empty."
        )

        return

    food_total = sum(
        item["price"] * item["quantity"]
        for item in cart
    )

    delivery_fee = 0

    total = food_total + delivery_fee

    location = context.user_data.get(
        "delivery_location",
        "Not selected"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Confirm Order",
                callback_data="confirm_order"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="cancel_checkout"
            )
        ]
    ]

    await update.message.reply_text(
        "🧾 ORDER SUMMARY\n\n"
        f"📍 Delivery Location: {location}\n"
        f"🍽️ Food Total: {food_total} ETB\n"
        f"🚴 Delivery Fee: {delivery_fee} ETB\n"
        f"💰 Total: {total} ETB\n\n"
        "💵 Payment Method: CASH ON DELIVERY\n\n"
        "Please check your order and confirm.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# CONFIRM ORDER + SAVE TO MYSQL
# =========================================================

async def confirm_order(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    print("🔥🔥🔥 CONFIRM ORDER FUNCTION CALLED 🔥🔥🔥")

    query = update.callback_query

    await query.answer()

    # =====================================================
    # GET CART
    # =====================================================

    cart = context.user_data.get(
        "cart",
        []
    )

    if not cart:

        await query.edit_message_text(
            "❌ Your cart is empty."
        )

        return ConversationHandler.END

    # =====================================================
    # GET TELEGRAM USER
    # =====================================================

    telegram_user = query.from_user

    telegram_id = telegram_user.id
    first_name = telegram_user.first_name or ""
    last_name = telegram_user.last_name
    username = telegram_user.username

    phone = context.user_data.get(
        "phone"
    )

    location = context.user_data.get(
        "delivery_location"
    )

    if not phone:

        await query.edit_message_text(
            "❌ Phone number is missing.\n\n"
            "Please start checkout again."
        )

        return ConversationHandler.END

    if not location:

        await query.edit_message_text(
            "❌ Delivery location is missing.\n\n"
            "Please start checkout again."
        )

        return ConversationHandler.END

    # =====================================================
    # CALCULATE TOTAL
    # =====================================================

    food_total = sum(
        item["price"] * item["quantity"]
        for item in cart
    )

    delivery_fee = 0

    total = food_total + delivery_fee

    # =====================================================
    # LOCATION
    # =====================================================

    fixed_locations = {
        "Grill Parking",
        "Boy Parking",
        "Central Library"
    }

    location_id = None
    custom_location = None

    if location not in fixed_locations:
        custom_location = location

    # =====================================================
    # DATABASE
    # =====================================================

    connection = None
    cursor = None

    try:

        print("🔵 TRYING TO CONNECT TO MYSQL...")

        connection = get_connection()

        print("🟢 MYSQL CONNECTION SUCCESSFUL")

        cursor = connection.cursor()

        # =================================================
        # 1. FIND USER
        # =================================================

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE telegram_id = %s
            """,
            (telegram_id,)
        )

        user_result = cursor.fetchone()

        # =================================================
        # USER EXISTS
        # =================================================

        if user_result:

            user_id = user_result[0]

            cursor.execute(
                """
                UPDATE users
                SET
                    first_name = %s,
                    last_name = %s,
                    username = %s,
                    phone = %s
                WHERE telegram_id = %s
                """,
                (
                    first_name,
                    last_name,
                    username,
                    phone,
                    telegram_id
                )
            )

            print("✅ Existing user updated:", user_id)

        # =================================================
        # NEW USER
        # =================================================

        else:

            cursor.execute(
                """
                INSERT INTO users
                (
                    telegram_id,
                    first_name,
                    last_name,
                    username,
                    phone
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    telegram_id,
                    first_name,
                    last_name,
                    username,
                    phone
                )
            )

            user_id = cursor.lastrowid

            print("✅ NEW USER CREATED:", user_id)

        # =================================================
        # 2. GET LOCATION ID
        # =================================================

        if location in fixed_locations:

            cursor.execute(
                """
                SELECT
                    location_id,
                    delivery_fee
                FROM delivery_locations
                WHERE location_name = %s
                """,
                (location,)
            )

            location_result = cursor.fetchone()

            if not location_result:

                connection.rollback()

                await query.edit_message_text(
                    f"❌ Location '{location}' "
                    "does not exist in the database.\n\n"
                    "Please contact the administrator."
                )

                return ConversationHandler.END

            location_id = location_result[0]

            delivery_fee = float(
                location_result[1]
            )

            total = food_total + delivery_fee

        print("✅ Location:", location)

        # =================================================
        # 3. INSERT ORDER
        # =================================================

        cursor.execute(
            """
            INSERT INTO orders
            (
                user_id,
                location_id,
                custom_location,
                phone,
                food_total,
                delivery_fee,
                total_amount,
                payment_method,
                order_status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                user_id,
                location_id,
                custom_location,
                phone,
                food_total,
                delivery_fee,
                total,
                "CASH_ON_DELIVERY",
                "CONFIRMED"
            )
        )

        order_id = cursor.lastrowid

        print("✅ ORDER CREATED:", order_id)

        # =================================================
        # 4. INSERT ORDER ITEMS
        # =================================================

        for item in cart:

            food_id = item["food_id"]
            food_name = item["name"]
            quantity = item["quantity"]
            unit_price = item["price"]

            subtotal = (
                unit_price * quantity
            )

            cursor.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    food_id,
                    food_name,
                    quantity,
                    unit_price,
                    subtotal
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    order_id,
                    food_id,
                    food_name,
                    quantity,
                    unit_price,
                    subtotal
                )
            )

        print("✅ ORDER ITEMS SAVED")

        # =================================================
        # 5. INSERT PAYMENT
        # =================================================

        cursor.execute(
            """
            INSERT INTO payments
            (
                order_id,
                payment_method,
                amount,
                payment_status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                order_id,
                "CASH_ON_DELIVERY",
                total,
                "PENDING"
            )
        )

        print("✅ PAYMENT SAVED")

        # =================================================
        # 6. COMMIT
        # =================================================

        connection.commit()

        print("🎉🎉🎉 ORDER SAVED SUCCESSFULLY 🎉🎉🎉")

        # =================================================
        # 7. CLOSE DATABASE
        # =================================================

        cursor.close()
        cursor = None

        connection.close()
        connection = None

        # =================================================
        # 8. CLEAR CART
        # =================================================

        context.user_data["cart"] = []

        # =================================================
        # 9. SHOW CONFIRMATION
        # =================================================

        order_number = f"WKU-{order_id}"

        await query.edit_message_text(
            "🎉 ORDER CONFIRMED!\n\n"
            f"🆔 Order: {order_number}\n"
            f"📱 Phone: {phone}\n"
            f"📍 Delivery Location: {location}\n\n"
            f"🍽️ Food Total: {food_total} ETB\n"
            f"🚴 Delivery Fee: {delivery_fee} ETB\n"
            f"💰 Total: {total} ETB\n\n"
            "💵 Payment: CASH ON DELIVERY\n"
            "📦 Status: CONFIRMED\n\n"
            "🏪 Your order will be sent to "
            "Catholic Church Restaurant.\n\n"
            "🚴 After the restaurant prepares your food, "
            "the delivery person will deliver it to your "
            "selected WKU location.\n\n"
            "❤️ Thank you for using WKU Catholic Eats!"
        )

        return ConversationHandler.END

    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except Exception as e:

        print("====================================")
        print("❌ ORDER DATABASE ERROR")
        print("ERROR:", e)
        print("====================================")

        if connection:

            try:
                connection.rollback()

            except Exception:
                pass

        await query.edit_message_text(
            "❌ Sorry, your order could not be saved.\n\n"
            "Please try again.\n\n"
            "If the problem continues, contact the administrator."
        )

        return ConversationHandler.END

    # =====================================================
    # CLOSE CONNECTION
    # =====================================================

    finally:

        if cursor:

            try:
                cursor.close()

            except Exception:
                pass

        if connection:

            try:
                connection.close()

            except Exception:
                pass


# =========================================================
# CANCEL CHECKOUT
# =========================================================

async def cancel_checkout(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    await query.edit_message_text(
        "❌ Checkout cancelled.\n\n"
        "Your cart is still saved."
    )

    return ConversationHandler.END


# =========================================================
# CANCEL COMMAND
# =========================================================

async def cancel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "❌ Checkout cancelled.\n\n"
        "Your cart is still saved.",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END