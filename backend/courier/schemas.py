import datetime
from dataclasses import dataclass
from typing import Literal


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
    order_id: int
    delivery_address: Location
    courier: int | None = None
    amount: float = 0
    status: Literal['searching', 'in-process', 'delivered', 'canceled'] = 'searching'
    started_at: datetime.datetime = datetime.datetime.now()
    completed_at: datetime.datetime | None = None
