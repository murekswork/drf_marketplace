import asyncio
import json
import threading
from abc import ABC, abstractmethod

from channels.consumer import get_channel_layer
from channels.generic.websocket import AsyncWebsocketConsumer
from kafka_common.receiver import SingletonMixin

from utils_.location_tracker import LocationTracker


class WebsocketMessageProvider(SingletonMixin):
    _message_queue: list = []

    def __init__(self, message_creators: list['MessageCreator'] | None = None) -> None:
        self._message_creators = message_creators

    async def get_messages_from_creators(self):
        if self._message_creators:
            for creator in self._message_creators:
                message = await creator.create_message()
                self._message_queue.append(message)

    async def get_next_message(self) -> str:
        if not self._message_queue:
            await asyncio.sleep(3)
            await self.get_messages_from_creators()
        message = self._message_queue.pop()
        return message


class WebsocketMessageSender(SingletonMixin):
    _messaging_activity: bool = False

    def __init__(self, message_provider: WebsocketMessageProvider) -> None:
        self.message_provider = message_provider

    async def trigger_messaging(self):
        await self.send_message_to_group_periodically()

    async def send_message_to_group_periodically(self):
        channel_layer = get_channel_layer()
        while True:
            if await self.get_messaging_activity():
                message = await self.message_provider.get_next_message()
                if message:
                    await channel_layer.group_send("observers", {
                        "type": "send_message",
                        "message": message
                    })

    @classmethod
    async def get_messaging_activity(cls):
        return cls._messaging_activity

    @classmethod
    async def set_messaging_activity(cls, value: bool):
        cls._messaging_activity = value
        return cls._messaging_activity


class WebsocketUsersManager(SingletonMixin):
    _observers: int = 0
    _message_sender = WebsocketMessageSender

    @classmethod
    async def _add_observer(cls):
        cls._observers += 1

    @classmethod
    async def _remove_observer(cls):
        cls._observers -= 1

    @classmethod
    async def _get_observers(cls):
        return cls._observers

    @classmethod
    async def connect(cls):
        await cls._add_observer()
        if not await cls._message_sender.get_messaging_activity():
            await cls._message_sender.set_messaging_activity(True)

    @classmethod
    async def disconnect(cls):
        await cls._remove_observer()
        if not await cls._get_observers():
            await cls._message_sender.set_messaging_activity(False)


class MapObservationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add("observers", self.channel_name)
        await self.accept()
        await WebsocketUsersManager.connect()

    async def disconnect(self, code):
        await WebsocketUsersManager.disconnect()
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


class MessageCreator(ABC):

    @abstractmethod
    async def create_message(self) -> str:
        raise NotImplementedError


class LocationMessageCreator(MessageCreator):

    def __init__(self):
        self.locator = LocationTracker()

    async def create_message(self) -> str:
        locations = self.locator.get_all_locations()
        message = json.dumps({'couriers': locations})
        return message


class WebsocketFacade:

    def __init__(
            self,
            message_creators: list[type[MessageCreator]],
            message_provider: type[WebsocketMessageProvider],
            message_sender: type[WebsocketMessageSender]):
        self.message_creators = message_creators
        self.message_provider = message_provider
        self.message_sender = message_sender

    async def _init_message_creators(self) -> list[MessageCreator]:
        creators = []
        for creator in self.message_creators:
            creators.append(creator())
        return creators

    async def _init_message_provider(self, *creators) -> WebsocketMessageProvider:
        provider = self.message_provider(*creators)
        return provider

    async def start_service(self):
        creators = await self._init_message_creators()
        provider = await self._init_message_provider(creators)
        sender = self.message_sender(provider)
        await sender.trigger_messaging()


def run_websocket():
    facade = WebsocketFacade(
        [LocationMessageCreator],
        WebsocketMessageProvider,
        WebsocketMessageSender
    )
    asyncio.run(
        facade.start_service()
    )


thread = threading.Thread(target=run_websocket, daemon=True)
thread.start()
