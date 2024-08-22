from django.contrib import admin

from bitrix_app.models import Lead
from api.mixins import ActiveAdminMixin


@admin.register(Lead)
class LeadAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "bitrix_id",
        "id",
        "title",
        "status",
    )
    list_filter = (
        "status",
    )
