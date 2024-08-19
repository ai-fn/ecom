from django.contrib import admin

from import_app.models import ImportTask, ImportSetting


@admin.register(ImportTask)
class ImportTaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "file",
        "status",
        "import_setting",
    )

@admin.register(ImportSetting)
class ImportSettingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
    )
