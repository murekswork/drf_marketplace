from django.urls import path

from . import views

urlpatterns = [
    path('<int:pk>/', views.DeliveryApiView.as_view(), name='delivery-detail'),
]
