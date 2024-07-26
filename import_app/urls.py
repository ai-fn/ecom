from rest_framework.routers import DefaultRouter

from django.urls import path, include

from import_app.views import ImportTaskViewSet, ImportSettingViewSet


router = DefaultRouter()
router.register(r"import-tasks", ImportTaskViewSet)
router.register(r"import-settings", ImportSettingViewSet)

app_name = "import_app"

urlpatterns = [path("", include(router.urls))]
