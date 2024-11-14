from django.urls import path, include

from rest_framework import routers

from cart import views
from cart.views import CartItemViewSet, OrderViewSet, PickupPointViewSet

router = routers.DefaultRouter()
router.register(r"cart", CartItemViewSet, basename="cart")
router.register(r"orders", OrderViewSet, basename="orders")
router.register(r"pickup-points", PickupPointViewSet, basename="pickup_points")

app_name = "cart"

urlpatterns = [
    path("", include(router.urls)),
    path("cart-count/", views.CartCountView.as_view(), name="cart-count"),
]
