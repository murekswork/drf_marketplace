from rest_framework.routers import DefaultRouter

from products.viewsets import ProductViewSet

router = DefaultRouter()
router.register(r'product-abc', viewset=ProductViewSet, basename='products')

urlpatterns = router.urls