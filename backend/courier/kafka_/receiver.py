import json
import logging

from bot.kafka_common.receiver import KafkaReceiver
from courier.kafka_.sender import send_courier_profile
from utils.location_tracker import LocationTracker


class CourierLocationReceiver(KafkaReceiver):
    _instance = None
    _thread = None
    _topic = 'courier_location'

    def __init__(self,):
        try:
            super().__init__()

            self.location_tracker = LocationTracker()
        except Exception as e:
            logging.error(f'(ERROR) GOT an exception while initializing Location Tracker {e}', exc_info=True)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def _consume(self, topic: str):
        self.consumer.subscribe([topic])
        while True:
            message = self.consumer.poll(timeout=1.0)
            if message is None:
                continue
            if message.error():
                continue
            msg = json.loads(message.value().decode('utf-8'))
            self.location_tracker.set_location(courier_id=msg['courier_id'], location=msg['location'])

        self.consumer.close()


class CourierProfileAskReceiver(KafkaReceiver):
    _instance = None
    _thread = None
    _topic = 'ask_courier_profile'

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance

    def _consume(self, topic: str):
        self.consumer.subscribe([self._topic])
        while True:
            message = self.consumer.poll()
            if message is None:
                continue
            if message.error():
                logging.error(f'ReceiverCourierProfileAsk error {message.error()}')
                continue

            request: dict = json.loads(message.value().decode('utf-8'))
            logging.info(f'(SUCCESS) Received message: {request}')

            send_courier_profile(request)

        self.consumer.close()
