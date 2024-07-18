from django.contrib import admin

from bitrix_app.models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bitrix_id",
        "title",
        "status",
    )
    list_filter = (
        "bitrix_id",
        "status",
    )
