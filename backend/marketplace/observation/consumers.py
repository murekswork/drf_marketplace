import asyncio
import json
import logging
import threading

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from kafka_common.receiver import SingletonMixin

from utils_.location_tracker import LocationTracker


class MapObservationProducer(SingletonMixin):
    _observers: int = 0
    _messaging_activity = False

    @classmethod
    async def add_observer(cls):
        cls._observers += 1

    @classmethod
    async def remove_observer(cls):
        cls._observers -= 1

    @classmethod
    async def get_observers(cls):
        return cls._observers

    @classmethod
    async def get_messaging_activity(cls):
        return cls._messaging_activity

    @classmethod
    async def set_messaging_activity(cls, value: bool):
        cls._messaging_activity = value
        return cls._messaging_activity

    @classmethod
    async def trigger_messaging(cls):
        await cls.send_message_to_group_periodically()

    @classmethod
    async def send_message_to_group_periodically(cls):
        channel_layer = get_channel_layer()
        locator = await cls.init_locator()
        logging.warning('Sending message to')
        while True:
            if await cls.get_messaging_activity():
                logging.warning('SENT MSG !')
                locations = locator.get_all_locations()
                message = json.dumps({'couriers': locations})
                await asyncio.sleep(3)
                await channel_layer.group_send("observers", {
                    "type": "send_message",
                    "message": message
                })

    @classmethod
    async def init_locator(cls):
        locator = LocationTracker()
        return locator

    @classmethod
    async def connect(cls):
        await cls.add_observer()
        if not await cls.get_messaging_activity():
            await cls.set_messaging_activity(True)

    @classmethod
    async def disconnect(cls):
        await cls.remove_observer()
        if not await cls.get_observers():
            await cls.set_messaging_activity(False)


class MapObservationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add("observers", self.channel_name)
        await self.accept()
        await MapObservationProducer.connect()

    async def disconnect(self, code):
        await MapObservationProducer.disconnect()
        await self.channel_layer.group_discard("observers", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.send(text_data=json.dumps({'message': message}))

    async def send_message(self, event):
        message = event["message"]
        await self.send(text_data=message)

    async def send_message_to_group(self, event):
        await self.send(text_data=event["message"])


def run():
    producer = MapObservationProducer()
    asyncio.run(producer.trigger_messaging())


thread = threading.Thread(target=run, daemon=True)
thread.start()
