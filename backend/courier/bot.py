import logging
from collections import defaultdict
from typing import DefaultDict

from courier.config import telegram_token
from courier.filters.filter import (
    NOT_ONLINE_COURIER_MESSAGE_FILTER,
    ONLINE_COURIER_ACTIVE_DELIVERY_FILTER,
    ONLINE_COURIER_LOCATION_FILTER,
    ONLINE_COURIER_MESSAGE_FILTER,
)
from courier.schemas import Courier, Delivery, Location
from courier.service.courier_orm_service import CourierOrmService
from courier.src.courier import DistanceCalculator
from courier.src.service import DeliveryLogic, couriers, deliveries
from telegram import Update
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    ExtBot,
    MessageHandler,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class ChatData:
    """Custom class for chat_data. Here we store data per message."""

    def __init__(self) -> None:
        self.clicks_per_message: DefaultDict[int, int] = defaultdict(int)


# The [ExtBot, dict, ChatData, dict] is for type checkers like mypy
class CustomContext(CallbackContext[ExtBot, dict, ChatData, dict]):
    """Custom class for context."""

    def __init__(
            self,
            application: Application,
            chat_id: int | None = None,
            user_id: int | None = None,
    ):
        super().__init__(application=application, chat_id=chat_id, user_id=user_id)
        self._message_id: int | None = None

    @property
    def bot_user_ids(self) -> set[int]:
        """Custom shortcut to access a value stored in the bot_data dict"""
        return self.bot_data.setdefault('user_ids', set())

    @property
    def message_clicks(self) -> int | None:
        """Access the number of clicks for the message this context object was built for."""
        if self._message_id:
            return self.chat_data.clicks_per_message[self._message_id]
        return None

    @message_clicks.setter
    def message_clicks(self, value: int) -> None:
        """Allow to change the count"""
        if not self._message_id:
            raise RuntimeError('There is no message associated with this context object.')
        self.chat_data.clicks_per_message[self._message_id] = value

    @classmethod
    def from_update(cls, update: object, application: 'Application') -> 'CustomContext':
        """Override from_update to set _message_id."""
        # Make sure to call super()
        context = super().from_update(update, application)

        if context.chat_data and isinstance(update, Update) and update.effective_message:
            # pylint: disable=protected-access
            context._message_id = update.effective_message.message_id

        # Remember to return the object
        return context


async def get_couriers_on_line(update: Update, context: CallbackContext):
    await update.message.reply_text(str(couriers))


async def courier_start_carrying(update: Update, context: CallbackContext):
    msg = update.message
    user = msg.chat
    try:
        c_tg = Courier(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )

        # Orm connection
        orm_service = CourierOrmService()
        c = await service.get_or_create_courier(c_tg)
        c_tg = await service.adapter.orm_to_tg(c)
        #
        
        d_service = DeliveryLogic()
        await d_service.add_courier(c_tg)
        # couriers[user.username] = c
        await msg.reply_text(f'\nSuccessfully added you to line! Send your location cast now! \n{c_tg}')
    # else:
    except Exception as e:
        logger.warning(f'{e}')
        await msg.reply_text('You are already on line stop doing dis!')


async def courier_stop_carrying(update: Update, context: CallbackContext):
    msg = update.message
    user = msg.chat
    try:
        c = couriers.pop(user.id)

        # Orm logic
        orm_service = CourierOrmService()
        c = await orm_service.update_courier(c)
        c_tg = await orm_service.adapter.orm_to_tg(c)
        #
        
        await msg.reply_text(f'Your smena successfully is done. Thanks!\n{c_tg.__dict__}')
        logger.info(f'Courier {user} successfully done his work')
    except Exception as e:
        logger.warning(e)
        await msg.reply_text(f'Your smena was not done yet. Please try again! {e}')


async def track_location(update: Update, context: CallbackContext):
    msg = update.edited_message
    user = msg.chat
    try:
        couriers[user.id].location = Location(lat=msg.location.latitude,
                                              lon=msg.location.longitude)
        logger.info(f'{user.first_name} {user.last_name} is moving')
    except Exception as e:
        logger.warning(e)


async def send_delivery_info_msg(context: CallbackContext, chat_id, delivery: Delivery):
    await context.bot.send_message(chat_id=chat_id, text=f'{delivery}')
    await context.bot.send_location(chat_id=chat_id, latitude=45.313346, longitude=43.562793)


async def distribute_deliveries_periodic_task(context: CallbackContext):
    service = DeliveryLogic()
    deliveries = service.start_delivering()
    logging.warning('Starting deliveries')
    
    if deliveries is not None:
        async for i in deliveries:
            logger.info(f'Got delivery {i} for delivering')
            if i:
                await send_delivery_info_msg(context, chat_id=i['courier'].id, delivery=i['delivery'])
            else:
                logger.warning('No free couriers!')
    else:
        logger.warning('Distribution does not started because of not free couriers!')


async def job_check_deliveries(update, context: CallbackContext):
    job_queue = context.job_queue
    job_queue.run_repeating(distribute_deliveries_periodic_task, interval=5, first=0)


async def show_couriers_delivery(update: Update, context: CallbackContext):
    cour_id = update.message.chat.id
    service = DeliveryLogic()
    d = await service.get_couriers_delivery(cour_id)
    if d:
        await update.message.reply_text(f'You delivery is {d}')
    else:
        await update.message.reply_text('You dont have any active deliveries!')


async def close_delivery(update: Update, context: CallbackContext):
    cour_id = update.message.chat.id
    service = DeliveryLogic()
    delivery = await service.get_couriers_delivery(courier_id=cour_id)
    if delivery:
        await service.close_delivery(delivery_id=delivery.id)
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


def main() -> None:
    """Run the bot."""
    context_types = ContextTypes(context=CustomContext, chat_data=ChatData)

    application = Application.builder().token(telegram_token).context_types(context_types).build()

    application.add_handler(MessageHandler(callback=track_location, filters=ONLINE_COURIER_LOCATION_FILTER))

    application.add_handler(CommandHandler(command='stop_carrying', callback=courier_stop_carrying,
                                           filters=ONLINE_COURIER_MESSAGE_FILTER)
                            )

    application.add_handler(CommandHandler(command='start_carrying', callback=courier_start_carrying,
                                           filters=NOT_ONLINE_COURIER_MESSAGE_FILTER))

    application.add_handler(CommandHandler(command='check_couriers', callback=get_couriers_on_line))

    application.add_handler(CommandHandler(command='current_delivery', callback=show_couriers_delivery,
                                           filters=ONLINE_COURIER_MESSAGE_FILTER))

    application.add_handler(CommandHandler(command='close_delivery', callback=close_delivery,
                                           filters=ONLINE_COURIER_ACTIVE_DELIVERY_FILTER))

    application.add_handler(CommandHandler(command='start', callback=job_check_deliveries))

    application.add_handler(CommandHandler(command='add_distance', callback=increase_delivery_distance))
    application.add_handler(CommandHandler(command='sub_distance', callback=decrease_delivery_distance))
    application.add_handler(CommandHandler(command='deliveries', callback=show_all_deliveries))

    application.run_polling(allowed_updates=Update.ALL_TYPES)