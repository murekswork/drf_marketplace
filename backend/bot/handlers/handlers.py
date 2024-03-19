import json
import logging
from dataclasses import asdict

from courier import DistanceCalculator
from kafka_tg.sender import CourierLocationSender, CourierProfileAsker, TgDeliverySender
from schemas import Delivery, Location, couriers, deliveries
from service import DeliveryLogic
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


async def courier_start_carrying(update: Update, context: CallbackContext):
    msg = update.message
    user = msg.chat
    try:
        c = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }

        kafka_ = CourierProfileAsker()
        kafka_.send(json.dumps(c))

        await msg.reply_text('Successfully added you to line! Send your location cast now!')
    except Exception as e:
        logger.warning(f'{e}')
        await msg.reply_text('You are already on line stop doing dis!')


async def courier_stop_carrying(update: Update, context: CallbackContext):
    msg = update.message
    user = msg.chat
    try:
        c = couriers.pop(user.id)
        await msg.reply_text(f'Your work is over. Thanks!\n{c.__dict__}')

        logger.info(f'Courier {user} successfully done his work')
    except Exception as e:
        logger.warning(e)
        await msg.reply_text('Your work is not done yet. Please try again later!')


async def track_location(update: Update, context: CallbackContext):
    msg = update.edited_message
    user = msg.chat
    try:
        # TODO: Return writing in couriers
        loc = Location(lat=msg.location.latitude, lon=msg.location.longitude)

        couriers[user.id].location = loc

        msg = {'courier_id': user.id, 'location': asdict(loc)}
        kafka_ = CourierLocationSender()
        kafka_.send(json.dumps(msg))

        logger.info(f'{user.first_name} {user.last_name} is moving')
    except Exception as exc:
        logger.warning(exc)


async def send_delivery_info_msg(context: CallbackContext, chat_id, delivery: Delivery):
    await context.bot.send_message(chat_id=chat_id, text=f'{delivery}')
    await context.bot.send_location(chat_id=chat_id, latitude=delivery.latitude, longitude=delivery.longitude)


async def distribute_deliveries_periodic_task(context: CallbackContext):
    service = DeliveryLogic()
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
    service = DeliveryLogic()
    d = await service.get_couriers_delivery(chat.id)
    await update.message.reply_text(f'You delivery is {d}')


async def close_delivery(update: Update, context: CallbackContext):
    cour_id = update.message.chat.id
    service = DeliveryLogic()
    delivery = await service.get_couriers_delivery(courier_id=cour_id)
    if delivery:
        await service.close_delivery(delivery_id=delivery.id)

        kafka_ = TgDeliverySender()
        kafka_.send_delivery_to_django(delivery)

        await update.message.reply_text('Delivery closed! Хорошая работа парниша')
        await update.message.reply_text(f'Your current delivery score is {couriers.get(cour_id, None)}')
    else:
        await update.message.reply_text('You dant have any deliveries!')


async def increase_delivery_distance(update: Update, context: CallbackContext):
    distance_calculator: DistanceCalculator = DistanceCalculator()
    distance_calculator.working_range += 3
    logger.info('Delivery distance is increased by 3 kms...')
    await update.message.reply_text('Delivery distance is increased by 3 kms...')


async def decrease_delivery_distance(update: Update, context: CallbackContext):
    distance_calculator: DistanceCalculator = DistanceCalculator()
    distance_calculator.working_range -= 3
    logger.info('Delivery distance is decreased by 3 kms...')
    await update.message.reply_text('Delivery distance is decreased by 3 kms...')


async def show_all_deliveries(update: Update, context: CallbackContext):
    await update.message.reply_text(f'All deliveries: {deliveries}')
