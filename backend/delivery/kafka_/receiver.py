import json
import logging

from bot.kafka_common.receiver import KafkaReceiver
from courier.kafka_.sender import send_courier_profile
from courier.services import CourierDeliveryService
from delivery.services.delivery_service import DeliveryFromTgAdapter


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

                # Updates delivery status in database
                d_service = DeliveryFromTgAdapter()
                d_db = d_service.update_delivery_status_from_telegram(d)

                # Updates courier status in database
                c_service = CourierDeliveryService()
                c_db = c_service.close_delivery(d_db)

                # Sends back updated courier data
                send_courier_profile({'id': c_db.id})

            except Exception as e:
                logging.error(f'Could not unparse incoming delivery msg to dataclass! {e}')
        self.consumer.close()
