import json
import logging

from kafka_common.receiver import KafkaReceiver
from schemas import Courier, Delivery, couriers, deliveries

# class KafkaReceiver:
#
#     def __init__(self):
#         self.consumer = Consumer({'bootstrap.servers': 'kafka:9092',
#                                   'group.id': 'my-consumer-group',
#                                   'auto.offset.reset': 'earliest'
#                                   })


class CourierProfileReceiver(KafkaReceiver):
    _instance = None
    _thread = None
    _topic = 'courier_profile'

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance

    # def __init__(self):
    #     super().__init__()
    #     try:
    #         self._start_consuming()
    #     except:
    #         time.sleep(10)
    #         self._start_consuming()
    #
    # def _start_consuming(self):
    #     if self._thread is None or not self._thread.is_alive():
    #         self._thread = threading.Thread(target=self._consume_forever, daemon=True)
    #         self._thread.start()
    #
    # def _consume_forever(self):
    #     while True:
    #         try:
    #             self.consume_profiles()
    #         except Exception as e:
    #             logging.error(e)
    #             self.consumer.close()
    #             time.sleep(5)

    def _consume(self, topic='courier_profile'):
        self.consumer.subscribe([topic])
        while True:
            message = self.consumer.poll(timeout=1.0)
            if message is None:
                continue
            if message.error():
                logging.error(message.error())
                continue

            msg = message.value().decode('utf-8')
            msg = json.loads(msg)
            c = msg['courier']

            cour = Courier(
                id=int(c['id']),
                username=c['username'],
                first_name=c['first_name'],
                last_name=c['last_name'],
                done_deliveries=c['done_deliveries'],
                balance=c['balance'],
                rank=c['rank']
            )

            couriers[cour.id] = cour
            logging.info(f'(SUCCESS) Got courier profile {cour} from django !')
        self.consumer.close()


class TgDeliveryReceiver(KafkaReceiver):
    _instance = None
    _thread = None
    _topic = 'to_deliver'

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance

    def _consume(self, topic: str = 'to_deliver'):
        self.consumer.subscribe([topic])
        while True:
            message = self.consumer.poll(timeout=1.0)
            if message is None:
                continue
            if message.error():
                logging.error(message.error())
                continue

            msg = message.value().decode('utf-8')
            msg = json.loads(msg)

            logging.info(f'(SUCCESS) Got incoming delivery {msg} from django !')
            try:
                d = Delivery(**msg['delivery'])
                deliveries[d.id] = d
            except Exception as e:
                logging.error(f'Could not unparse incoming delivery msg to dataclass! {e}')
        self.consumer.close()
