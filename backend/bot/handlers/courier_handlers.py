from decorators import exception_logging
from handlers.common_handlers import profile_handler
from keyboards import CourierReplyMarkups
from replies import Replies
from services.courier_service import CourierService
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext


@exception_logging
async def track_location_handler(update: Update, context: CallbackContext, first=False):
    user = update.edited_message.chat
    service = CourierService()
    await service.track_location(update.edited_message, user)
    if first:
        await update.message.reply_text(
            text=Replies.COURIER_SENT_LOCATION_INFO,
            reply_markup=CourierReplyMarkups.COURIER_MAIN_MARKUP,
        )


@exception_logging
async def courier_start_carrying_handler(update: Update, context: CallbackContext):
    user = update.message.chat
    service = CourierService()
    await service.courier_start_carrying(user)
    await update.message.reply_text(
        text=Replies.COURIER_START_CARRYING_INFO,
        parse_mode=ParseMode.HTML,
        reply_markup=CourierReplyMarkups.COURIER_RECEIVE_LOCATION_MARKUP,
    )


@exception_logging
async def courier_stop_carrying_handler(update: Update, context: CallbackContext):
    user = update.message.chat
    service = CourierService()
    await service.courier_stop_carrying(user)
    await update.message.reply_text(
        Replies.STOP_CARRYING_INFO, reply_markup=CourierReplyMarkups.NOT_CARRYING_MARKUP
    )
    await profile_handler(update, context)