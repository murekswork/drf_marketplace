import datetime

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from decorators import exception_logging
from handlers.common_handlers import profile_handler
from keyboards import CourierReplyMarkups
from replies import Replies
from schemas.schemas import Delivery, Courier
from services.courier_service import CourierService
from services.delivery_service import DeliveryService


@exception_logging
async def picked_up_delivery_handler(update: Update, context: CallbackContext):
    courier_id = update.message.chat.id
    service = DeliveryService()
    delivery = await service.picked_up_delivery(courier_id)

    await context.bot.send_location(
        chat_id=courier_id,
        latitude=delivery.consumer_latitude,
        longitude=delivery.consumer_longitude,
    )
    await context.bot.send_message(
        chat_id=courier_id,
        text=Replies.PICKED_UP_DELIVERY_INFO,
        reply_markup=CourierReplyMarkups.PICKED_UP_DELIVERY_MARKUP,
    )


@exception_logging
async def close_delivery(update: Update, context: CallbackContext, status: int):
    cour_id = update.message.chat.id
    service = CourierService()
    delivery = await service.close_delivery(cour_id, status)
    await update.message.reply_text(
        Replies.CLOSED_DELIVERY_INFO.format(delivery.status),
        reply_markup=CourierReplyMarkups.COURIER_MAIN_MARKUP,
    )
    await profile_handler(update, context)


@exception_logging
async def send_delivery_pickup_point_msg(context: CallbackContext, chat_id, lat, lon):
    await context.bot.send_location(chat_id=chat_id, latitude=lat, longitude=lon)
    await context.bot.send_message(
        chat_id=chat_id,
        text=Replies.PICKUP_MSG_INFO,
        reply_markup=CourierReplyMarkups.GOT_DELIVERY_MARKUP,
    )


@exception_logging
async def show_couriers_delivery(update: Update, context: CallbackContext):
    chat = update.message.chat
    service = DeliveryService()
    d = await service.get_couriers_delivery(chat.id)
    await update.message.reply_text(Replies.CURRENT_DELIVERY_INFO.format(d))


@exception_logging
async def send_delivery_info_msg(context: CallbackContext, chat_id, delivery: Delivery):
    await send_delivery_pickup_point_msg(
        context, chat_id, delivery.consumer_latitude, delivery.consumer_longitude
    )
    msg = Replies.DELIVERY_INFO.format(
        minutes=(delivery.estimated_time - datetime.datetime.now()).total_seconds()
        / 60,
        amount=delivery.amount,
        status=delivery.status,
        address=delivery.address,
        estimated_time=delivery.estimated_time,
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text=msg,
        parse_mode=ParseMode.HTML,
        reply_markup=CourierReplyMarkups.GOT_DELIVERY_MARKUP,
    )


@exception_logging
async def delivery_taking_late_notification(
    context: CallbackContext, delivery: Delivery
):
    await context.bot.send_message(
        chat_id=delivery.courier,
        text=Replies.DELIVERY_TAKING_LATE_NOTIFICATION.format(
            delivery.id,
            (delivery.estimated_time - datetime.datetime.now()).total_seconds() / 360,
        ),
    )


@exception_logging
async def delivery_cancelled_by_consumer_notification(
    context: CallbackContext, courier: Courier
):
    await context.bot.send_message(
        chat_id=courier.id, text=Replies.DELIVERY_CANCELLED_BY_CONSUMER_NOTIFICATION
    )


@exception_logging
async def delivery_time_out_notification(context: CallbackContext, delivery: Delivery):
    await context.bot.send_message(
        chat_id=delivery.courier, text=Replies.DELIVERY_TIME_OUT_NOTIFICATION
    )
