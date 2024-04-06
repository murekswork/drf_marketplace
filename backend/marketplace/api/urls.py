from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("auth/", obtain_auth_token, name="token-auth"),
    path("", views.api_home),
    path("deliveries/", include("delivery.urls")),
    path("categories/", include("category.urls")),
    path("products/", include("products.urls")),
    path("articles/", include("articles.urls")),
    path("wallet/", include("wallet.urls")),
    path("orders/", include("order.urls")),
    path("shops/", include("shop.urls")),
]
