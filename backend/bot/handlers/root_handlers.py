from decorators import exception_logging
from schemas.schemas import couriers, deliveries
from services.delivery_service import DeliveryService
from telegram import Update
from telegram.ext import CallbackContext


@exception_logging
async def change_delivery_distance_handler(
    update: Update, context: CallbackContext, distance: int
):
    service = DeliveryService()
    service.change_delivery_distance(distance)
    await update.message.reply_text(text=f'Delivery distance increased by {distance}')


@exception_logging
async def show_all_deliveries(update: Update, context: CallbackContext):
    await update.message.reply_text(text=f'All deliveries: {deliveries}')


@exception_logging
async def get_couriers_on_line(update: Update, context: CallbackContext):
    await update.message.reply_text(str(couriers))
