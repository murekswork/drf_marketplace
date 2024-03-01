from django.urls import path
from . import views


urlpatterns = [
    path('', views.WalletAPIView.as_view(), name='wallet'),
    path('create/', views.CreateWalletAPIView.as_view(), name='wallet-create')
]