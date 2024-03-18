import threading
from abc import abstractmethod
from os import getenv

from confluent_kafka import Consumer


class KafkaReceiver:
    _thread = None
    _topic = None

    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': f'{getenv("KAFKA_HOST")}:{getenv("KAFKA_PORT")}',
            'group.id': 'my-consumer-group',
            'auto.offset.reset': 'earliest'
        })

    @abstractmethod
    def _consume(self, topic: str):
        raise NotImplementedError

    def start_listening(self):
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._consume, args=(self._topic,), daemon=True)
            self._thread.start()
            threading.get_ident()
