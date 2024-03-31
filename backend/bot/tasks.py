from handlers.delivery_handlers import (
    delivery_taking_late_notification,
    delivery_time_out_notification,
    send_delivery_info_msg,
)
from keyboards import CourierReplyMarkups
from logging_.logger import logger
from services.delivery_service import DeliveryService
from services.metrics_service import AvgCourierSpeedProvider
from services.notification_service import NotificationService
from telegram import Update
from telegram.ext import CallbackContext
from utils import DistanceCalculator


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
    to_notify_deliveries, time_out_deliveries = await service.distribute_notifications()
    for delivery in to_notify_deliveries:
        await delivery_taking_late_notification(context, delivery)
    for delivery in time_out_deliveries:
        await delivery_time_out_notification(context, delivery)


async def job_check_deliveries(update: Update, context: CallbackContext):
    await update.message.reply_text(text='Select action', reply_markup=CourierReplyMarkups.COURIER_MAIN_MARKUP)
    job_queue = context.job_queue
    job_queue.run_repeating(distribute_deliveries_periodic_task, interval=5, first=0)


async def job_notify_courier(update: Update, context: CallbackContext):
    job_queue = context.job_queue
    job_queue.run_repeating(delivery_notification_periodic_task, interval=10, first=0)


async def collect_speed_metrics(update):
    metrics_collector = AvgCourierSpeedProvider()
    speed = await metrics_collector.get_avg_couriers_speed()
    if speed:
        await DistanceCalculator.set_avg_courier_speed(speed)


async def job_get_avg_couriers_speed(update: Update, context: CallbackContext):
    job_queue = context.job_queue
    job_queue.run_repeating(collect_speed_metrics, interval=360, first=0)


async def run_jobs(update: Update, context: CallbackContext):
    await job_get_avg_couriers_speed(update, context)
    await job_notify_courier(update, context)
    await job_check_deliveries(update, context)
