import datetime

from telegram import Location, Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from decorators import exception_logging
from handlers.common_handlers import profile_handler
from keyboards import CourierReplyMarkups
from replies import Replies
from schemas.schemas import Courier, Delivery
from services.courier_service import CourierService
from services.delivery_service import DeliveryService, DeliveryValidationService


@exception_logging
async def picked_up_delivery_handler(update: Update, context: CallbackContext):
    user = update.message.chat

    validation_service = DeliveryValidationService(user.id)
    if await validation_service.validate_courier_on_point() is not True:
        await context.bot.send_message(
            chat_id=user.id,
            text=Replies.DELIVERY_COURIER_NOT_ON_REQUIRED_POINT_ANSWER
        )
        return

    service = DeliveryService()
    delivery = await service.picked_up_delivery(user.id)

    await context.bot.send_location(
        chat_id=user.id,
        latitude=delivery.consumer_latitude,
        longitude=delivery.consumer_longitude,
    )
    await context.bot.send_message(
        chat_id=user.id,
        text=Replies.PICKED_UP_DELIVERY_INFO,
        reply_markup=CourierReplyMarkups.PICKED_UP_DELIVERY_MARKUP,
    )


@exception_logging
async def close_delivery(update: Update, context: CallbackContext, status: int):
    user = update.message.chat

    validation_service = DeliveryValidationService(user.id)
    if await validation_service.validate_courier_on_point() is not True:
        await context.bot.send_message(
            chat_id=user.id,
            text=Replies.DELIVERY_COURIER_NOT_ON_REQUIRED_POINT_ANSWER
        )
        return

    service = CourierService()
    delivery = await service.close_delivery(user.id, status)
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
    user = update.message.chat
    service = DeliveryService()
    delivery = await service.get_couriers_delivery(user.id)
    if delivery.status == 3:
        point = Location(delivery.longitude, delivery.latitude)
    else:
        point = Location(delivery.consumer_longitude, delivery.consumer_latitude)

    await update.message.reply_location(point.latitude, point.longitude)
    await update.message.reply_text(Replies.CURRENT_DELIVERY_INFO.format(delivery))


@exception_logging
async def send_delivery_info_msg(context: CallbackContext, chat_id, delivery: Delivery):
    await send_delivery_pickup_point_msg(
        context,
        chat_id,
        delivery.consumer_latitude,
        delivery.consumer_longitude
    )
    msg = Replies.DELIVERY_INFO.format(
        minutes=round(
            (delivery.estimated_time - datetime.datetime.now()).total_seconds() / 60, 2
        ),
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
            round((delivery.estimated_time - datetime.datetime.now()).total_seconds() / 60, 2)
        ),
    )


@exception_logging
async def delivery_cancelled_by_consumer_notification(
        context: CallbackContext, courier: Courier
):
    await context.bot.send_message(
        chat_id=courier.id,
        text=Replies.DELIVERY_CANCELLED_BY_CONSUMER_NOTIFICATION,
        reply_markup=CourierReplyMarkups.CARRYING_NOT_DELIVERY_MARKUP
    )


@exception_logging
async def delivery_time_out_notification(context: CallbackContext, delivery: Delivery):
    await context.bot.send_message(
        chat_id=delivery.courier, text=Replies.DELIVERY_TIME_OUT_NOTIFICATION
    )
