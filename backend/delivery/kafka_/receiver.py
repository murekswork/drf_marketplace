import json
import logging

from bot.kafka_common.receiver import KafkaReceiver
from delivery.models import Delivery


class DjangoDeliveryReceiver(KafkaReceiver):
    _instance = None
    _thread = None
    _topic = 'delivered'

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance

    def _consume(self, topic: str = 'delivered'):
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
                d = msg['delivery']
                self.update_delivery_in_db(d)

            except Exception as e:
                logging.error(f'Could not unparse incoming delivery msg to dataclass! {e}')
        self.consumer.close()

    def update_delivery_in_db(self, delivery_dict: dict):
        try:
            cour_id = delivery_dict.pop('courier')
            delivery_dict['courier_id'] = cour_id
            d = Delivery.objects.filter(id=delivery_dict['id']).first()
            if d:
                for key, value in delivery_dict.items():
                    setattr(d, key, value)
                logging.info('(SUCCESS) Updated delivery in database!')
                d.save()
        except Exception as e:
            logging.error(f'Could not update delivery in database! coz of {e}')
