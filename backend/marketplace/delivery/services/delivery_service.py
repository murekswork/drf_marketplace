import logging
from abc import ABC, abstractmethod

from delivery.models import Delivery


class DeliveryUtils:

    def update_delivery_in_db_from_telegrma(self, delivery_dict: dict) -> Delivery:
        try:
            cour_id = delivery_dict.pop('courier')
            delivery_dict['courier_id'] = cour_id
            d = Delivery.objects.filter(id=delivery_dict['id']).first()
            if d:
                for key, value in delivery_dict.items():
                    setattr(d, key, value)
                logging.info('(SUCCESS) Updated delivery in database!')
                d.save()
            return d
        except Exception as e:
            logging.error(f'Could not update delivery in db coz of {e}', exc_info=True)
