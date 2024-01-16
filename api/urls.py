from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views

from api import views
from api.views import (
    CharacteristicValueViewSet,
    CharacteristicViewSet,
    MyTokenObtainPairView,
    PriceViewSet,
    ProductViewSet,
    ReviewViewSet,
    SettingViewSet,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r"products", ProductViewSet)
router.register(r"reviews", ReviewViewSet)
router.register(r"characteristics", CharacteristicViewSet)
router.register(r"characteristics-values", CharacteristicValueViewSet)
router.register(r"prices", PriceViewSet)
router.register(r"settings", SettingViewSet)

urlpatterns = [
    path("", include(router.urls)),  # Including router URLs here
    path("login", MyTokenObtainPairView.as_view()),
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
