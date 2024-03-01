from django.urls import path
from . import views


urlpatterns = [
    path('', views.OrderListCreateAPIView.as_view(), name='order-list'),
    path('<uuid:pk>/payment', views.OrderPayAPIView.as_view(), name='order-payment'),
]