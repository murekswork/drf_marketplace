from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import DeliveryViewSet

delivery_router = SimpleRouter()
delivery_router.register(prefix="deliveries", viewset=DeliveryViewSet)


urlpatterns = [
    path("", include(delivery_router.urls)),
]