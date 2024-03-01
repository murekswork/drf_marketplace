from django.urls import path

from . import views

urlpatterns = [
    path('', views.CategoryListAPIView.as_view(), name='category-list'),
    path('<str:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),

]
