import logging

from keyboards import CommonMarkups, CourierReplyMarkups
from replies import Replies
from schemas.schemas import Delivery, couriers, deliveries
from services.courier_service import CourierService
from services.delivery_service import DeliveryService
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def get_couriers_on_line(update: Update, context: CallbackContext):
    await update.message.reply_text(str(couriers))


async def courier_start_carrying_handler(update: Update, context: CallbackContext):
    msg = update.message
    user = msg.chat
    try:
        service = CourierService()
        await service.courier_start_carrying(user)
        await msg.reply_text(text=Replies.COURIER_START_CARRYING_INFO,
                             parse_mode=ParseMode.HTML,
                             reply_markup=CourierReplyMarkups.COURIER_RECEIVE_LOCATION_MARKUP)
    except Exception as e:
        logger.error(e)


async def profile_handler(update: Update, context: CallbackContext):
    user = update.message.chat
    await update.message.reply_html(text=Replies.COURIER_PROFILE_INFO.format(**couriers.get(int(user.id)).__dict__))


async def courier_stop_carrying(update: Update, context: CallbackContext):
    # TODO: VIEW LAYER SHOULD NOT HAVE DIRECT ACCESS TO REPO! FIX IT
    msg = update.message
    user = msg.chat
    try:
        couriers.pop(user.id)
        await msg.reply_text(Replies.STOP_CARRYING_INFO,
                             reply_markup=CourierReplyMarkups.NOT_CARRYING_MARKUP)
        logger.info(f'Courier {user} successfully done his work')
    except Exception as e:
        logger.warning(e)


async def track_location_handler(update: Update, context: CallbackContext, first=None):
    msg = update.edited_message
    user = msg.chat
    try:
        service = CourierService()
        await service.track_location(msg, user)
        if first:
            await msg.reply_text(text=Replies.COURIER_SENT_LOCATION_INFO,
                                 reply_markup=CourierReplyMarkups.COURIER_MAIN_MARKUP)
        logger.info(f'{user.first_name} {user.last_name} is moving')
    except Exception as e:
        logger.warning(e)


async def got_it_handler(update: Update):
    await update.message.reply_text('')


async def send_delivery_info_msg(context: CallbackContext, chat_id, delivery: Delivery):
    await send_delivery_pickup_point_msg(
        context,
        chat_id,
        delivery.consumer_latitude,
        delivery.consumer_longitude
    )
    # TODO: TO REFACTOR!
    await context.bot.send_message(chat_id=chat_id,
                                   text=Replies.DELIVERY_INFO.format(
                                       id=delivery.id,
                                       latitude=delivery.latitude,
                                       longitude=delivery.longitude,
                                       courier=delivery.courier,
                                       amount=delivery.amount,
                                       status=delivery.status,
                                       started_at=delivery.started_at,
                                       address=delivery.address,
                                       estimated_time=delivery.estimated_time),
                                   parse_mode=ParseMode.HTML,
                                   reply_markup=CourierReplyMarkups.GOT_DELIVERY_MARKUP
                                   )


async def picked_up_delivery_handler(update: Update, context: CallbackContext):
    try:
        courier_id = update.message.chat.id
        service = DeliveryService()
        delivery = await service.picked_up_delivery(courier_id)

        await context.bot.send_location(
            chat_id=courier_id,
            latitude=delivery.consumer_latitude,
            longitude=delivery.consumer_longitude
        )
        await context.bot.send_message(
            chat_id=courier_id,
            text=Replies.PICKED_UP_DELIVERY_INFO,
            reply_markup=CourierReplyMarkups.PICKED_UP_DELIVERY_MARKUP)

    except Exception as e:
        logger.error(f'Could not receiver pickup point msg coz of, {e}', exc_info=True)


async def send_delivery_pickup_point_msg(context: CallbackContext, chat_id, lat, lon):
    await context.bot.send_location(
        chat_id=chat_id,
        latitude=lat,
        longitude=lon
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text=Replies.PICKUP_MSG_INFO,
        reply_markup=CourierReplyMarkups.GOT_DELIVERY_MARKUP
    )


async def show_couriers_delivery(update: Update, context: CallbackContext):
    chat = update.message.chat
    service = DeliveryService()
    d = await service.get_couriers_delivery(chat.id)
    await update.message.reply_text(Replies.CURRENT_DELIVERY_INFO.format(d))


async def close_delivery(update: Update, context: CallbackContext, status: int):
    cour_id = update.message.chat.id
    service = CourierService()
    delivery = await service.close_delivery(cour_id, status)
    await update.message.reply_text(Replies.CLOSED_DELIVERY_INFO.format(delivery.status),
                                    reply_markup=CourierReplyMarkups.COURIER_MAIN_MARKUP)
    await profile_handler(update, context)


async def change_delivery_distance_handler(update: Update, context: CallbackContext, distance: int):
    service = DeliveryService()
    service.change_delivery_distance(distance)
    msg = f'Delivery distance is increased by {distance} kms...'
    logger.info(msg)
    await update.message.reply_text(msg)


async def show_all_deliveries(update: Update, context: CallbackContext):
    await update.message.reply_text(f'All deliveries: {deliveries}')


async def start_bot(update: Update, context: CallbackContext):
    await update.message.reply_text(text='Welcome!', reply_markup=CommonMarkups.MAIN_MARKUP)
