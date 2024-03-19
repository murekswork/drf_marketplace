import logging
import threading

from confluent_kafka import Producer


class KafkaSender:
    _topic = None

    def __init__(self):
        # self._topic = topic
        self.config = {
            'bootstrap.servers': 'kafka:9092',
            'group.id': 'my-group',
            'auto.offset.reset': 'earliest'
        }
        self.producer = Producer(self.config)
        self.send_thread = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def send_message(self, msg: str):
        # msg here shud be jsonified !!!
        def msg_callback(err, msg):
            if err is not None:
                self.logger.error(f'{msg.topic()} delivery failed {err}')
            else:
                self.logger.info(f'(SUCCESS) Message from {self.__class__} with {msg.value()} topic {msg.topic()}!')

        if not self.send_thread or not self.send_thread.is_alive():
            self.send_thread = threading.Thread(target=self._msg_wrapper, args=(msg, msg_callback))
            self.send_thread.start()
            threading.get_ident()

    def _msg_wrapper(self, msg: str, callback):
        try:
            self.logger.error(f'CURRENT TOPIC IS {self._topic}')
            self.producer.produce(self._topic, msg.encode('utf-8'), callback=callback)
            self.producer.flush()
        except Exception as e:
            self.logger.error(f'Error sending message {e}', exc_info=True)

    def send(self, msg: str):
        # msg here shud be jsonified !!!
        try:
            self.send_message(msg)
        except Exception as e:
            logging.error(f'Could not send msg from {self.__class__.__name__} coz of {e}')
