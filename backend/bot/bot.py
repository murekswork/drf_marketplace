import logging
import threading
import time
from os import getenv

from filter import CourierFilters
from handlers.handlers import (
    change_delivery_distance_handler,
    close_delivery,
    courier_start_carrying_handler,
    courier_stop_carrying,
    get_couriers_on_line,
    picked_up_delivery_handler,
    show_all_deliveries,
    show_couriers_delivery,
    track_location_handler,
)
from tasks import job_check_deliveries
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(f'{getenv("BOT_TOKEN")}').build()

    application.add_handler(
        MessageHandler(
            callback=track_location_handler,
            filters=CourierFilters.ONLINE_COURIER_LOCATION_FILTER)
    )

    application.add_handler(
        CommandHandler(
            command='stop_carrying',
            callback=courier_stop_carrying,
            filters=CourierFilters.ONLINE_COURIER_MESSAGE_FILTER
        )
    )

    application.add_handler(
        CommandHandler(
            command='start_carrying',
            callback=courier_start_carrying_handler,
            filters=CourierFilters.NOT_ONLINE_COURIER_MESSAGE_FILTER)
    )

    application.add_handler(
        CommandHandler(
            command='check_couriers',
            callback=get_couriers_on_line)
    )

    application.add_handler(
        CommandHandler(
            command='current_delivery',
            callback=show_couriers_delivery,
            filters=CourierFilters.ONLINE_COURIER_MESSAGE_FILTER)
    )

    application.add_handler(
        CommandHandler(
            command='close_delivery',
            callback=lambda update, context: close_delivery(update, context, 5),
            filters=CourierFilters.ONLINE_COURIER_ACTIVE_DELIVERY_FILTER)
    )

    application.add_handler(
        CommandHandler(
            command='cancel_delivery',
            callback=lambda update, context: close_delivery(update, context, 0),
            filters=CourierFilters.ONLINE_COURIER_ACTIVE_DELIVERY_FILTER)
    )

    application.add_handler(
        CommandHandler(
            command='picked_up',
            callback=picked_up_delivery_handler,
            filters=CourierFilters.ONLINE_COURIER_ACTIVE_DELIVERY_FILTER)
    )

    application.add_handler(
        CommandHandler(
            command='start',
            callback=job_check_deliveries)
    )

    application.add_handler(
        CommandHandler(
            command='add_distance',
            callback=lambda update, context: change_delivery_distance_handler(update, context, 3))
    )

    application.add_handler(
        CommandHandler(
            command='sub_distance',
            callback=lambda update, context: change_delivery_distance_handler(update, context, 3))
    )

    application.add_handler(
        CommandHandler(
            command='deliveries',
            callback=show_all_deliveries)
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


def listen_for_courier_profile():
    threading.get_ident()
    receiver = CourierProfileReceiver()
    receiver.start_listening()


def listen_for_delivery():
    threading.get_ident()
    listener = TgDeliveryReceiver()
    listener.start_listening()


if __name__ == '__main__':
    from kafka_tg.receiver import CourierProfileReceiver, TgDeliveryReceiver

    time.sleep(10)
    try:
        listen_for_courier_profile()
        listen_for_delivery()
        main()
    except Exception as e:
        logging.error(f'Could not start bot or tg listeners! {e}, {e.args}', exc_info=True)
