import logging

from schemas.schemas import Delivery, couriers, deliveries
from services.courier_service import CourierService
from services.delivery_service import DeliveryService
from telegram import Update
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
        await msg.reply_text('Successfully added you to line! Send your location cast now!')
    except Exception as e:
        logger.warning(e)


async def courier_stop_carrying(update: Update, context: CallbackContext):
    msg = update.message
    user = msg.chat
    try:
        c = couriers.pop(user.id)
        await msg.reply_text(f'Your work is over. Thanks {c.__dict__}')
        logger.info(f'Courier {user} successfully done his work')
    except Exception as e:
        logger.warning(e)


async def track_location_handler(update: Update, context: CallbackContext):
    msg = update.edited_message
    user = msg.chat
    try:
        service = CourierService()
        await service.track_location(msg, user)
        logger.info(f'{user.first_name} {user.last_name} is moving')
    except Exception as e:
        logger.warning(e)


async def send_delivery_info_msg(context: CallbackContext, chat_id, delivery: Delivery):
    await context.bot.send_message(chat_id=chat_id, text=f'{delivery}')
    await send_delivery_pickup_point_msg(
        context,
        chat_id,
        delivery.consumer_latitude,
        delivery.consumer_longitude
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
            parse_mode='HTML',
            text='Nice job! Now you should bring picked up good you take to client in location below')

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
        parse_mode='HTML',
        text='You should pick up goods on point under this msg'
    )


async def show_couriers_delivery(update: Update, context: CallbackContext):
    chat = update.message.chat
    service = DeliveryService()
    d = await service.get_couriers_delivery(chat.id)
    await update.message.reply_text(f'You delivery is {d}')


async def close_delivery(update: Update, context: CallbackContext, status: int):
    cour_id = update.message.chat.id
    service = CourierService()
    delivery = await service.close_delivery(cour_id, status)
    if delivery:
        await update.message.reply_text(f'Delivery closed with status {status}!')
        await update.message.reply_text(f'Your score will be updated soon! {couriers.get(cour_id, None)}')
    else:
        await update.message.reply_text('You dont have any deliveries!')


async def change_delivery_distance_handler(update: Update, context: CallbackContext, distance: int):
    service = DeliveryService()
    service.change_delivery_distance(distance)
    msg = f'Delivery distance is increased by {distance} kms...'
    logger.info(msg)
    await update.message.reply_text(msg)


async def show_all_deliveries(update: Update, context: CallbackContext):
    await update.message.reply_text(f'All deliveries: {deliveries}')
