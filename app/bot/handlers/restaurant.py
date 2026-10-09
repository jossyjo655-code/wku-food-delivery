from telegram import Update
from telegram.ext import ContextTypes


async def restaurant_order_notification(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # We will connect this to MySQL later.
    print("New restaurant order received.")