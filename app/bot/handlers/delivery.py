from telegram import Update
from telegram.ext import ContextTypes


async def delivery_notification(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Delivery functionality will be connected
    # after the order system is working.

    print("New delivery order received.")