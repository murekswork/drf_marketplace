from django.urls import path

from . import views

urlpatterns = [
    path('<str:slug>/', views.ShopDetailAPIView.as_view(), name='shop-detail'),
    path('', views.ShopListAPIView.as_view(), name='shop-list'),
    path(
        '<str:slug>/upload_products/',
        views.UploadsAPIVIew.as_view(),
        name='upload-list',
    ),
    path(
        '<str:slug>/upload_products/csv',
        views.UploadCSVProductsAPIView.as_view(),
        name='upload-csv',
    ),
    path(
        '<str:slug>/upload_products/results/<int:pk>/',
        views.UploadCSVProductsAPIView.as_view(),
        name='upload-detail',
    ),
]
