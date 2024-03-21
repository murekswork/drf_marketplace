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
    msg = update.message
    user = msg.chat
    try:
        service = CourierService()
        await service.track_location(msg, user)
        logger.info(f'{user.first_name} {user.last_name} is moving')
    except Exception as e:
        logger.warning(e)


async def send_delivery_info_msg(context: CallbackContext, chat_id, delivery: Delivery):
    await context.bot.send_message(chat_id=chat_id, text=f'{delivery}')
    await context.bot.send_location(chat_id=chat_id, latitude=delivery.latitude, longitude=delivery.longitude)


async def distribute_deliveries_periodic_task(context: CallbackContext):
    service = DeliveryService()
    deliveries_ = service.start_delivering()
    logging.warning('Starting deliveries')

    if deliveries is not None:
        async for i in deliveries_:
            logger.info(f'Got delivery {i} for delivering')
            if i['success'] is True:
                await send_delivery_info_msg(context, chat_id=i['courier'].id, delivery=i['delivery'])
            else:
                logger.warning('No free couriers!')
    else:
        logger.warning('Distribution does not started because of not free couriers!')


async def job_check_deliveries(update, context: CallbackContext):
    job_queue = context.job_queue
    job_queue.run_repeating(distribute_deliveries_periodic_task, interval=5, first=0)


async def show_couriers_delivery(update: Update, context: CallbackContext):
    chat = update.message.chat
    service = DeliveryService()
    d = await service.get_couriers_delivery(chat.id)
    await update.message.reply_text(f'You delivery is {d}')


async def close_delivery(update: Update, context: CallbackContext, status: int):
    cour_id = update.message.chat.id
    service = CourierService()
    delivery = service.close_delivery(cour_id, status)
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
