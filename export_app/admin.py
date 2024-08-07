from django.contrib import admin

from export_app.models import ExportSettings, ExportTask

@admin.register(ExportSettings)
class ExportSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )

@admin.register(ExportTask)
class ExportTaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "export_status",
        "ended_at",
    )
    list_filter = (
        "export_status",
    )
