from products.viewsets import ProductViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"product-abc", viewset=ProductViewSet, basename="products")

urlpatterns = router.urls
