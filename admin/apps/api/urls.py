from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CartView, CategoryViewSet, FAQViewSet, OrderView, ProductViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("faq", FAQViewSet, basename="faq")

urlpatterns = router.urls + [
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/<int:item_id>/", CartView.as_view(), name="cart-item"),
    path("orders/", OrderView.as_view(), name="orders"),
    path("orders/<int:order_id>/", OrderView.as_view(), name="order-detail"),
]
