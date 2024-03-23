from repository.abc_repository import DictRepositoryImpl
from schemas.schemas import couriers


class CourierRepository(DictRepositoryImpl):

    source = couriers
