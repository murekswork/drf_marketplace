from repository.abc_repository import DictRepositoryImpl
from schemas.schemas import deliveries


class DeliveryRepository(DictRepositoryImpl):
    source = deliveries
