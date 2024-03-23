import logging

from handlers.handlers import logger, send_delivery_info_msg
from keyboards import CourierReplyMarkups
from schemas.schemas import deliveries
from services.delivery_service import DeliveryService
from telegram import Update
from telegram.ext import CallbackContext


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


async def job_check_deliveries(update: Update, context: CallbackContext):
    await update.message.reply_text(text='Select action', reply_markup=CourierReplyMarkups.COURIER_MAIN_MARKUP)
    job_queue = context.job_queue
    job_queue.run_repeating(distribute_deliveries_periodic_task, interval=5, first=0)
