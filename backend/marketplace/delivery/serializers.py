from rest_framework import serializers
from utils_.location_tracker import LocationTracker

from .models import Delivery


class CourierSerializer(serializers.Serializer):

    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)


class DeliverySerializer(serializers.ModelSerializer):

    courier = serializers.SerializerMethodField(read_only=True)

    def get_courier(self, obj: Delivery):
        location_tracker = LocationTracker()
        if obj.courier:
            location = location_tracker.get_location(str(obj.courier_id))
            serialized_c = CourierSerializer(obj.courier)
            if location:
                serialized_c.data["latitude"] = location["lat"]
                serialized_c.data["longitude"] = location["lon"]
            return serialized_c.data
        return "No courier"

    class Meta:
        model = Delivery
        fields = "__all__"
