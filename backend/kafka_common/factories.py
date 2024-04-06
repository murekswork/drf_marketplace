from kafka_common.sender import KafkaSender


def producer_factory(topic: str) -> KafkaSender:
    sender = KafkaSender(topic)
    return sender
