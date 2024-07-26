from django.contrib import admin

from import_app.models import ImportTask, ImportSetting


@admin.register(ImportTask)
class ImportTaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "file",
        "status",
    )

@admin.register(ImportSetting)
class ImportSettingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "import_task",
        "name",
        "slug",
    )
