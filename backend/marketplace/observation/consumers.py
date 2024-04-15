import json

from channels.generic.websocket import AsyncWebsocketConsumer

from observation.services.service import WebsocketUsersManager


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
