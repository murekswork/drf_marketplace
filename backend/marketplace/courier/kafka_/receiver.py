import json

from courier.kafka_.sender import send_courier_profile_from_django_to_telegram
from kafka_common.receiver import KafkaReceiver
from kafka_common.topics import CourierTopics
from utils_.location_tracker import LocationTracker


class CourierLocationReceiver(KafkaReceiver):
    _topic = CourierTopics.COURIER_LOCATION

    def __init__(self):
        super().__init__()
        self.location_tracker = LocationTracker()

    def post_consume_action(self, msg: str):
        msg_dict = json.loads(msg)
        self.location_tracker.set_location(
            courier_id=msg_dict['courier_id'], location=msg_dict['location']
        )


class CourierProfileAskReceiver(KafkaReceiver):
    _topic = CourierTopics.COURIER_PROFILE_ASK

    def post_consume_action(self, msg: str):
        msg = json.loads(msg)
        send_courier_profile_from_django_to_telegram(msg)
