import threading

from kafka_tg.receiver import TgDeliveryToCancelReceiver, TgDeliveryReceiver, CourierProfileReceiver


def listen_for_courier_profile():
    threading.get_ident()
    receiver = CourierProfileReceiver()
    receiver.start_listening()


def listen_for_delivery():
    threading.get_ident()
    listener = TgDeliveryReceiver()
    listener.start_listening()


def listen_for_cancelled_deliveries():
    threading.get_ident()
    listener = TgDeliveryToCancelReceiver()
    listener.start_listening()