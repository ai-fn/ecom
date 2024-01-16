from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views

from api import views
from api.views import (
    MyTokenObtainPairView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = routers.DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),  # Including router URLs here
    path("login", MyTokenObtainPairView.as_view()),
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
