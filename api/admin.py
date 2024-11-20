from django.contrib import admin
from api.models import ApiKey


@admin.register(ApiKey)
class ApiTokenAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client_id",
        "created_at",
        "updated_at",
        "is_active",
    )
