from django.contrib import admin

from bitrix_app.models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "bitrix_id",
        "id",
        "title",
        "status",
    )
    list_filter = (
        "status",
    )
