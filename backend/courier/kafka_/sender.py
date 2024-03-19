import json
import logging
from dataclasses import asdict

from bot.kafka_common.receiver import SingletonMixin
from bot.kafka_common.sender import KafkaSender
from courier.models import Courier
from courier.schemas import CourierTG
from utils.adapters import model_to_dataclass_converter

# def orm_to_tg_adapter(courier: Courier) -> CourierTG:
#     try:
#         return CourierTG(
#             username=courier.username,
#             id=courier.id,
#             first_name=courier.first_name,
#             last_name=courier.last_name,
#             balance=float(courier.balance),
#             rank=float(courier.rank),
#             done_deliveries=courier.done_deliveries
#         )
#     except Exception as e:
#         print(e)
#         logging.warning(e)


def send_courier_profile_from_django_to_telegram(courier_dict: dict):
    try:
        c = Courier.objects.filter(id=courier_dict['id']).first()
        if c is None:
            if not courier_dict['username']:
                courier_dict['username'] = courier_dict['first_name'] + courier_dict['last_name']
            c = Courier.objects.create(**courier_dict)

        c_tg = model_to_dataclass_converter(c, CourierTG)
        msg = {
            'courier_id': c_tg.id,
            'courier': asdict(c_tg)
        }
        msg['courier']['balance'] = float(msg['courier']['balance'])

        producer = CourierProfileProducer()
        producer.send(msg=json.dumps(msg))

    except Exception as e:
        logging.error(f'Could not send courier profile from Django to Tg, coz of {e}')


class CourierProfileProducer(KafkaSender, SingletonMixin):
    _topic = 'courier_profile'
