from django.contrib import admin

from api.mixins import ActiveAdminMixin
from export_app.models import ExportSettings, ExportTask

@admin.register(ExportSettings)
class ExportSettingsAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )

@admin.register(ExportTask)
class ExportTaskAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "export_status",
        "ended_at",
    )
    list_filter = (
        "export_status",
    )
