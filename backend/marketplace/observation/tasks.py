import asyncio
import logging

import channels
from channels.layers import get_channel_layer

# async def start_messaging():
    # channel_layer = channels.layers.get_channel_layer()
    # asyncio.set_event_loop(asyncio.new_event_loop())
    # loop = asyncio.get_event_loop()
    # loop.create_task(send_message_to_group_periodically())
    # loop.run_forever()
