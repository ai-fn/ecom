from django.urls import path, include

from rest_framework.routers import DefaultRouter

from bitrix_app.views import LeadViewSet


router = DefaultRouter()
router.register(r"leads", LeadViewSet)

app_name = "bitrix"
urlpatterns = [
    path("", include(router.urls))
]
