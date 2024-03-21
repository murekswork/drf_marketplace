import logging
import threading

from confluent_kafka import Producer


class KafkaSender:
    _topic: str

    def __init__(self):
        # self._topic = topic
        self.config = {
            'bootstrap.servers': 'kafka:9092',
            'group.id': 'my-group',
            'auto.offset.reset': 'earliest'
        }
        self.producer = Producer(self.config)
        self.send_thread = None
        self.logger = logging.getLogger(f'{self._topic.upper()}: {self.__class__.__name__}')

    def _send_message(self, msg: str):
        """Sends a message via the producer."""
        # msg here shud be jsonified !!!
        def msg_callback(err, msg):
            if err is not None:
                self.logger.error(f'{msg.topic()} delivery failed {err}')
            else:
                self.logger.info(f'Message from {self.__class__} with {msg.value()} topic {msg.topic()}!')

        if not self.send_thread or not self.send_thread.is_alive():
            self.send_thread = threading.Thread(target=self._msg_wrapper, args=(msg, msg_callback))
            self.send_thread.start()
            threading.get_ident()

    def _msg_wrapper(self, msg: str, callback):
        """Wrapper for sending a message via the producer"""
        try:
            self.producer.produce(self._topic, msg.encode('utf-8'), callback=callback)
            self.producer.flush()
        except Exception:
            self.logger.error(f'Sending message {msg} with {self._topic.upper()}', exc_info=True)

    def send(self, msg: str):
        """Interface method to send a message via the producer with exception handling"""
        try:
            self._send_message(msg)
        except Exception:
            self.logger.error(f'Could not send msg <{msg}> with {self._topic.upper()}', exc_info=True)
