import datetime
from dataclasses import dataclass


@dataclass
class Location:
    lat: float
    lon: float


@dataclass
class Courier:
    id: int
    username: str
    first_name: str
    last_name: str
    location: Location | None = None
    busy: bool = False
    current_delivery_id: int | None = None
    done_deliveries: int = 0
    balance: float = 0
    rank: float = 5


@dataclass
class Delivery:
    id: int
    latitude: float
    longitude: float
    consumer_latitude: float | None = None
    consumer_longitude: float | None = None
    courier: int | None = None
    amount: float = 0
    status: int = 1
    started_at: datetime.datetime | str = datetime.datetime.now()
    completed_at: datetime.datetime | None = None
    address: str = ''
    priority: int = 0
    estimated_time: datetime.datetime | None = None
    last_notification_ts: datetime.datetime | None = None
    distance: float = 0


deliveries: dict[Delivery, None] = {}
delivering: dict[Delivery, None] = {}
couriers: dict[Courier, None] = {}
