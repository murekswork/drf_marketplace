from kafka_common.sender import KafkaSender


def producer_factory(topic: str) -> KafkaSender:
    sender = KafkaSender(topic)
    return sender


async def async_send_kafka_msg(msg: str, topic: str) -> None:
    if isinstance(msg, str) and isinstance(topic, str):
        producer = producer_factory(topic)
        producer.send(msg)
    else:
        raise ValueError("Invalid message type for kafka producer!")


def send_kafka_msg(msg: str, topic: str) -> None:
    if isinstance(msg, str) and isinstance(topic, str):
        producer = producer_factory(topic)
        producer.send(msg)
    else:
        raise ValueError("Invalid message type for kafka producer!")
