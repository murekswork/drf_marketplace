import logging
import threading
import time
from os import getenv

from filter import (
    NOT_ONLINE_COURIER_MESSAGE_FILTER,
    ONLINE_COURIER_ACTIVE_DELIVERY_FILTER,
    ONLINE_COURIER_LOCATION_FILTER,
    ONLINE_COURIER_MESSAGE_FILTER,
)
from handlers.handlers import (
    Application,
    CommandHandler,
    MessageHandler,
    close_delivery,
    courier_start_carrying,
    courier_stop_carrying,
    decrease_delivery_distance,
    get_couriers_on_line,
    increase_delivery_distance,
    job_check_deliveries,
    show_all_deliveries,
    show_couriers_delivery,
    track_location,
)
from telegram import Update


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(f'{getenv("BOT_TOKEN")}').build()

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
