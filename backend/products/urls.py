from django.urls import path

from . import views

urlpatterns = [
    path('<int:pk>', views.ProductDetailAPIView.as_view(), name='product-detail'),
    path('<int:pk>/delete', views.ProductDeleteAPIView.as_view(), name='product-delete'),
    path('<int:pk>/update', views.ProductUpdateAPIView.as_view(), name='product-update'),
    path('', views.ProductListCreateAPIView.as_view(), name='product-list'),
    path('my/', views.ProductListMyAPIView.as_view(), name='product-my'),
]