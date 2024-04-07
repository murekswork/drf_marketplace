from dataclasses import dataclass


@dataclass
class DeliveryTopics:
    TO_DELIVER = 'to_deliver'
    TO_CANCEL_DELIVERY = 'to_cancel_delivery'
    DELIVERED = 'delivered'


@dataclass
class CourierTopics:
    COURIER_LOCATION = 'courier_location'
    COURIER_PROFILE_ASK = 'ask_courier_profile'
    COURIER_PROFILE = 'courier_profile'
