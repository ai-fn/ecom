from django.urls import path, include

from rest_framework import routers

from cart import views
from .views import CartItemViewSet, OrderViewSet

router = routers.DefaultRouter()
router.register(r"cart", CartItemViewSet, basename='cart')
router.register(r"orders", OrderViewSet, basename="orders")

app_name = "cart"

urlpatterns = [
    path("", include(router.urls)),
    path(
        "add/",
        views.add_to_cart,
        name="add_to_cart",
    ),
]
