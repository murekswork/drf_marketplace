from handlers.delivery_handlers import (
    delivery_taking_late_notification,
    send_delivery_info_msg,
)
from keyboards import CourierReplyMarkups
from logging_.logger import logger
from services.delivery_service import DeliveryService
from services.notification_service import NotificationService
from telegram import Update
from telegram.ext import CallbackContext


async def distribute_deliveries_periodic_task(context: CallbackContext):
    service = DeliveryService()
    deliveries_ = await service.start_delivering()
    logger.warning('Starting deliveries')

    if deliveries_ is not None:
        async for delivery in deliveries_:
            logger.info(f'Got delivery {delivery} for delivering')
            if delivery['success']:
                await send_delivery_info_msg(context, chat_id=delivery['courier'].id, delivery=delivery['delivery'])
            else:
                logger.warning('No free couriers!')
    else:
        logger.warning('Distribution does not started because of not free couriers!')


async def delivery_notification_periodic_task(context: CallbackContext):
    service = NotificationService()
    to_notify_deliveries = await service.distribute_notifications()
    for delivery in to_notify_deliveries:
        await delivery_taking_late_notification(context, delivery)


async def job_check_deliveries(update: Update, context: CallbackContext):
    await update.message.reply_text(text='Select action', reply_markup=CourierReplyMarkups.COURIER_MAIN_MARKUP)
    job_queue = context.job_queue
    job_queue.run_repeating(distribute_deliveries_periodic_task, interval=5, first=0)


async def job_notify_courier(update: Update, context: CallbackContext):
    job_queue = context.job_queue
    job_queue.run_repeating(delivery_notification_periodic_task, interval=5, first=0)
