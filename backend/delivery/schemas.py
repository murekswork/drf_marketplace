import datetime
from dataclasses import dataclass

# from delivery.models import Delivery

# def delivery_orm_to_dataclass(delivery_orm: Delivery):
#     try:
#         return DeliveryDTO(
#             id=delivery_orm.id,
#             address=delivery_orm.address,
#             latitude=delivery_orm.latitude,
#             longitude=delivery_orm.longitude,
#             amount=delivery_orm.amount,
#             started_at=delivery_orm.started_at,
#             completed_at=delivery_orm.completed_at
#         )
#     except Exception as e:
#         logging.warning(f'Could not convert Delivery from ORM to DTO! {e}')


@dataclass
class DeliveryDTO:
    id: int
    address: str
    latitude: float
    longitude: float
    amount: float
    courier: int | None
    started_at: datetime.datetime | None
    completed_at: datetime.datetime | None
