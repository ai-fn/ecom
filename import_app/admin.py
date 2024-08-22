from django.contrib import admin

from api.mixins import ActiveAdminMixin
from import_app.models import ImportTask, ImportSetting


@admin.register(ImportTask)
class ImportTaskAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "file",
        "status",
        "import_setting",
    )

@admin.register(ImportSetting)
class ImportSettingAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
    )
