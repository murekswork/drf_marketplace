import logging
import threading

from confluent_kafka import Producer


class KafkaSender:

    def __init__(self):
        self.config = {
            'bootstrap.servers': 'kafka:9092',
            'group.id': 'my-group',
            'auto.offset.reset': 'earliest'
        }
        self.producer = Producer(self.config)
        self.send_thread = None

    def send_message(self, msg: str, topic: str):
        # msg here shud be jsonified !!!

        def msg_callback(err, msg):
            if err is not None:
                logging.error(f'{msg.topic()} delivery failed {err}')
            else:
                logging.info(f'(SUCCESS) Message from {self.__class__} with {msg.value()} topic {msg.topic()}!')

        if not self.send_thread or not self.send_thread.is_alive():
            self.send_thread = threading.Thread(target=self._msg_wrapper, args=(msg, topic, msg_callback))
            self.send_thread.start()
            threading.get_ident()

    def _msg_wrapper(self, msg: str, topic, callback):
        try:
            self.producer.produce(topic, msg.encode('utf'), callback=callback)
            self.producer.flush()
        except Exception as e:
            logging.error(f'Error sending location, {e}')

    def send(self, msg: str):
        raise NotImplementedError
