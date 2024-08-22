from django.contrib import admin

from blog.models import (
    Article,
    Feedback,
)
from api.mixins import ActiveAdminMixin


@admin.register(Article)
class ArticleAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = ("name", "created")
    filter_horizontal = ("products",)


@admin.register(Feedback)
class FeedbackAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "status",
    )
    list_filter = (
        "email",
        "status",
    )
