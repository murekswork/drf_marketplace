import logging
from dataclasses import asdict, dataclass

from courier.models import Courier
from courier.schemas import Courier as CourierTG


@dataclass
class CourierORM:
    id: int
    username: str
    first_name: str
    last_name: str
    balance: float
    rank: float = 5
    done_deliveries: int = 0


async def tg_to_orm_adapter(courier: CourierTG) -> CourierORM:
    return CourierORM(
        id=courier.id,
        username=courier.username,
        first_name=courier.first_name,
        last_name=courier.last_name,
        balance=courier.balance,
        rank=courier.balance,
        done_deliveries=courier.done_deliveries
    )


async def orm_to_tg_adapter(courier: Courier) -> CourierTG:
    try:
        return CourierTG(
            username=courier.username,
            id=courier.id,
            first_name=courier.first_name,
            last_name=courier.last_name,
            balance=float(courier.balance),
            rank=float(courier.rank),
            done_deliveries=courier.done_deliveries
        )
    except Exception as e:
        print(e)
        logging.warning(e)


# def orm_to_tg_adapter(courier: CourierORM) -> CourierTG: return
# TODO: WRITE THIS LATER

class CourierOrmService:

    def __init__(self):
        self.adapter = CourierAdapter()

    async def get_or_create_courier(self, courier: CourierTG) -> Courier:
        c_orm = await tg_to_orm_adapter(courier)
        try:
            c = await Courier.objects.aget(id=c_orm.id)

        except Exception as e:
            logging.warning(e)
            c = await Courier.objects.acreate(**asdict(c_orm))

        return c

    async def update_courier(self, courier: CourierTG) -> Courier:
        c = await self.get_or_create_courier(courier)

        c.balance = courier.balance

        c.done_deliveries = courier.done_deliveries

        await c.asave()

        return c


class CourierAdapter:

    async def orm_to_tg(self, courier: Courier) -> CourierTG:

        c = await orm_to_tg_adapter(courier)

        return c

    # async def tg_to_orm_adapter(self, courier: CourierTG) -> CourierORM:
    #
