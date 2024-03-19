import logging
import threading
from abc import abstractmethod
from os import getenv

from confluent_kafka import Consumer


class SingletonMixin:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance


class KafkaReceiver(SingletonMixin):
    _thread = None
    _topic = None

    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': f'{getenv("KAFKA_HOST")}:{getenv("KAFKA_PORT")}',
            'group.id': 'my-consumer-group',
            'auto.offset.reset': 'earliest'
        })
        self.logger = logging.getLogger(name=self.__class__.__name__)

    def _consume(self, topic: str = 'delivered'):
        self.consumer.subscribe([topic])
        while True:
            message = self.consumer.poll(timeout=1.0)
            if message is None:
                continue
            if message.error():
                logging.error(message.error())
                continue

            msg: str = message.value().decode('utf-8')

            # msg = json.loads(msg)

            self.logger.info(f'(SUCCESS) Got incoming delivery {msg} from django !')
            try:
                self.post_consume_action(msg)
                # d = msg['delivery']
                #
                # # Updates delivery status in database
                # d_service = DeliveryFromTgAdapter()
                # d_db = d_service.update_delivery_status_from_telegram(d)
                #
                # # Updates courier status in database
                # c_service = CourierDeliveryService()
                # c_db = c_service.close_delivery(d_db)
                #
                # # Sends back updated courier data
                # send_courier_profile({'id': c_db.id})

            except Exception as e:
                self.logger.error(f'Could not complete post consume action! {e}', exc_info=True)
        self.consumer.close()

    def start_listening(self):
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._consume, args=(self._topic,), daemon=True)
            self._thread.start()
            threading.get_ident()

    @abstractmethod
    def post_consume_action(self, msg: str):
        raise NotImplementedError
