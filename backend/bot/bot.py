import logging
import threading
import time
from os import getenv

from filter import CourierFilters
from handlers.common_handlers import profile_handler, start_bot
from handlers.courier_handlers import (
    courier_start_carrying_handler,
    courier_stop_carrying_handler,
    track_location_handler,
)
from handlers.delivery_handlers import (
    close_delivery,
    picked_up_delivery_handler,
    show_couriers_delivery,
)
from handlers.root_handlers import (
    change_delivery_distance_handler,
    get_couriers_on_line,
    show_all_deliveries,
)
from telegram.ext import Application, CommandHandler, MessageHandler
from telegram.ext.filters import Regex


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(f'{getenv("BOT_TOKEN")}').build()

    application.add_handler(
        MessageHandler(
            callback=track_location_handler,
            filters=CourierFilters.ONLINE_COURIER_LOCATION_FILTER,
        )
    )

    application.add_handler(
        MessageHandler(
            callback=lambda update, context: track_location_handler(
                update, context, True
            ),
            filters=CourierFilters.ONLINE_COURIER_FIRST_LOCATION_FILTER,
        )
    )

    application.add_handler(
        MessageHandler(
            callback=courier_stop_carrying_handler,
            filters=Regex('Stop carrying')
            & CourierFilters.ONLINE_COURIER_MESSAGE_FILTER,
        )
    )

    application.add_handler(
        MessageHandler(
            callback=courier_start_carrying_handler,
            filters=Regex(pattern='Start carrying')
            & CourierFilters.NOT_ONLINE_COURIER_MESSAGE_FILTER,
        )
    )

    application.add_handler(CommandHandler(command='start', callback=start_bot))

    application.add_handler(
        CommandHandler(command='check_couriers', callback=get_couriers_on_line)
    )

    application.add_handler(
        MessageHandler(
            callback=show_couriers_delivery,
            filters=Regex('Show delivery')
            & CourierFilters.ONLINE_COURIER_MESSAGE_FILTER,
        )
    )

    application.add_handler(
        MessageHandler(
            callback=lambda update, context: close_delivery(update, context, 5),
            filters=Regex('Delivered!')
            & CourierFilters.ONLINE_COURIER_ACTIVE_DELIVERY_FILTER,
        )
    )

    application.add_handler(
        MessageHandler(
            callback=lambda update, context: close_delivery(update, context, 0),
            filters=Regex('Cancel delivery')
            & CourierFilters.ONLINE_COURIER_ACTIVE_DELIVERY_FILTER,
        )
    )

    application.add_handler(
        MessageHandler(
            callback=picked_up_delivery_handler,
            filters=Regex('Picked up')
            & CourierFilters.ONLINE_COURIER_ACTIVE_DELIVERY_FILTER,
        )
    )
    from tasks import (
        job_check_deliveries,
        job_get_avg_couriers_speed,
        job_notify_courier,
        run_jobs,
    )

    application.add_handler(CommandHandler(command='runjobs', callback=run_jobs))

    application.add_handler(
        CommandHandler(command='start_task', callback=job_check_deliveries)
    )

    application.add_handler(
        CommandHandler(command='starttask', callback=job_notify_courier)
    )

    application.add_handler(
        CommandHandler(command='avgspeed', callback=job_get_avg_couriers_speed)
    )

    application.add_handler(
        MessageHandler(
            callback=profile_handler,
            filters=Regex(pattern='Show profile')
            & CourierFilters.ONLINE_COURIER_MESSAGE_FILTER,
        )
    )

    application.add_handler(
        CommandHandler(
            command='add_distance',
            callback=lambda update, context: change_delivery_distance_handler(
                update, context, 3
            ),
        )
    )

    application.add_handler(
        CommandHandler(
            command='sub_distance',
            callback=lambda update, context: change_delivery_distance_handler(
                update, context, 3
            ),
        )
    )

    application.add_handler(
        CommandHandler(command='deliveries', callback=show_all_deliveries)
    )

    application.run_polling()


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
        logging.error(
            f'Could not start bot or tg listeners! {e}, {e.args}', exc_info=True
        )
