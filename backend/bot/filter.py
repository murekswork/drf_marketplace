from telegram import Message
from telegram.ext.filters import MessageFilter, _Location


class _CouriersFilter(MessageFilter):

    def filter(self, message: Message) -> bool:
        from schemas import couriers
        return message.chat.id in couriers


class _OnlineCouriersLocationFilter(_Location, _CouriersFilter):

    def filter(self, message: Message) -> bool:
        res = _Location.filter(self, message) and _CouriersFilter.filter(self, message)
        return res
        # return message.chat.username in couriers.keys() and super().filter(message)


class _OnlineCourierMessageFilter(MessageFilter):

    def filter(self, message: Message) -> bool:
        from schemas import couriers
        return message.chat.id in couriers


class _OnlineNotLocationCourierMessageFilter(_OnlineCourierMessageFilter):

    def filter(self, message: Message):
        from schemas import couriers
        return message.chat.username in couriers and couriers[message.chat.username].location is None


class _NoActiveDeliveryFilter(_CouriersFilter):

    def filter(self, message: Message) -> bool:
        from schemas import couriers
        active_delivery = couriers.get(message.chat.username).busy
        return super().filter(message) and not active_delivery


class _ActiveDeliveryFilter(_CouriersFilter):

    def filter(self, message: Message) -> bool:
        from schemas import couriers
        is_courier = super().filter(message)
        # active_delivery = couriers.get(message.chat.username).busy
        if is_courier:
            return couriers.get(message.chat.id).busy
        return is_courier


class _NotOnlineCourierFilter(_CouriersFilter):

    def filter(self, message: Message) -> bool:
        # return True
        return not super().filter(message)


NOT_ONLINE_COURIER_MESSAGE_FILTER = _NotOnlineCourierFilter(name='not_online_courier')
ONLINE_COURIER_LOCATION_FILTER = _OnlineCouriersLocationFilter(name='courier_location')
ONLINE_COURIER_NOT_LOCATION_MESSAGE_FILTER = _OnlineNotLocationCourierMessageFilter(name='not_courier_filter')
ONLINE_COURIER_MESSAGE_FILTER = _OnlineCourierMessageFilter(name='courier_filter')
ONLINE_COURIER_NOT_ACTIVE_DELIVERY_FILTER = _NoActiveDeliveryFilter(name='courier_not_active_delivery')
ONLINE_COURIER_ACTIVE_DELIVERY_FILTER = _ActiveDeliveryFilter(name='courier_active_delivery')
