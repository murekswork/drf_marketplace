from decorators import exception_logging
from keyboards import CourierReplyMarkups
from logging_.logger import logger
from replies import Replies
from schemas.schemas import couriers
from services.courier_service import CourierService
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext


@exception_logging
async def track_location_handler(update: Update, context: CallbackContext, first=None):
    msg = update.edited_message
    user = msg.chat
    service = CourierService()
    await service.track_location(msg, user)
    if first:
        await msg.reply_text(
            text=Replies.COURIER_SENT_LOCATION_INFO,
            reply_markup=CourierReplyMarkups.COURIER_MAIN_MARKUP)


@exception_logging
async def courier_start_carrying_handler(update: Update, context: CallbackContext):
    msg = update.message
    user = msg.chat
    service = CourierService()
    await service.courier_start_carrying(user)
    await msg.reply_text(
        text=Replies.COURIER_START_CARRYING_INFO,
        parse_mode=ParseMode.HTML,
        reply_markup=CourierReplyMarkups.COURIER_RECEIVE_LOCATION_MARKUP)


@exception_logging
async def courier_stop_carrying(update: Update, context: CallbackContext):
    # TODO: VIEW LAYER SHOULD NOT HAVE DIRECT ACCESS TO REPO! FIX IT
    msg = update.message
    user = msg.chat
    service = CourierService()
    service.courier_stop_carrying()
    couriers.pop(user.id)
    await msg.reply_text(Replies.STOP_CARRYING_INFO,
                         reply_markup=CourierReplyMarkups.NOT_CARRYING_MARKUP)
    logger.info(f'Courier {user} successfully done his work')
