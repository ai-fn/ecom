from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    FeedbackViewSet,
)

router = DefaultRouter()
router.register(r"feedback", FeedbackViewSet)

app_name = "blog"

urlpatterns = [
    path("", include(router.urls))
]
