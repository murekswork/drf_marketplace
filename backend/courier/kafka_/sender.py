import json
import logging
from dataclasses import asdict

from bot.kafka_common.sender import KafkaSender
from courier.models import Courier
from courier.schemas import CourierTG


def orm_to_tg_adapter(courier: Courier) -> CourierTG:
    try:
        return CourierTG(
            username=courier.username,
            id=courier.id,
            first_name=courier.first_name,
            last_name=courier.last_name,
            balance=float(courier.balance),
            rank=float(courier.rank),
            done_deliveries=courier.done_deliveries
        )
    except Exception as e:
        print(e)
        logging.warning(e)


def send_courier_profile(courier_dict: dict):
    try:
        c = Courier.objects.filter(id=courier_dict['id']).first()
        if c is None:
            if not courier_dict['username']:
                courier_dict['username'] = courier_dict['first_name'] + courier_dict['last_name']
            c = Courier.objects.create(**courier_dict)
        c_tg = orm_to_tg_adapter(c)

        msg = {
            'courier_id': c_tg.id,
            'courier': asdict(c_tg)
        }

        sender = SendCourierProfile()
        sender.send(msg=json.dumps(msg))
    except Exception as e:
        logging.error(f'Could not send courier profile from Django to Tg, coz of {e}')


class SendCourierProfile(KafkaSender):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def send(self, msg: str):
        # msg here shud be jsonified !!!
        try:
            self.send_message(msg, topic='courier_profile')
        except Exception as e:
            print(e)
    # def send_profile(self, courier: dict):
    #     thread = threading.Thread(target=self._send_profiles, args=[courier])
    #     thread.start()
    #
    # def _send_profiles(self, courier: dict):
    #     try:
    #         self._send_courier_profile(courier)
    #     except Exception as e:
    #         print(e)
