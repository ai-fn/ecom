from django.urls import path, include
from rest_framework.routers import DefaultRouter

from export_app.http.export_task.viewsets import ExportTaskViewSet
from export_app.http.export_task_settings.viewsets import ExportSettingsViewSet

router = DefaultRouter()
router.register(r"export-tasks", ExportTaskViewSet)
router.register(r"export-settings", ExportSettingsViewSet)

app_name = "export_app"

urlpatterns = [
    path("", include(router.urls))
]
