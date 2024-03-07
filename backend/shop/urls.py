from django.urls import path

from . import views

urlpatterns = [
    path('<int:pk>/', views.ShopDetailAPIView.as_view(), name='shop-detail'),
    path('', views.ShopListAPIView.as_view(), name='shop-list'),
    path('upload_products/csv', views.UploadCSVProductsAPIView.as_view(), name='upload-csv'),
    path('upload_products/results/<int:pk>', views.UploadCSVProductsAPIView.as_view(), name='upload-detail'),
    path('upload_products/', views.UploadsAPIVIew.as_view(), name='upload-list')
]