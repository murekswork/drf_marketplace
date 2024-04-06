import json
import logging

from redis import Redis

redis_locator = Redis(host='redis', port=6379)


class LocationTracker:

    def __init__(self):
        self.redis: Redis = redis_locator

    def set_location(self, courier_id: str, location: dict[str, str]):
        self.redis.set(courier_id, json.dumps(location))

    def get_location(self, courier_id: str) -> dict[str, str]:
        try:
            location = self.redis.get(courier_id)
            return json.loads(location)
        except TypeError as e:
            logging.error(f'Could not fetch courier location {e}')
            return None
