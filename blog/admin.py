from django.contrib import admin

from blog.models import (
    Article,
    Feedback,
)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("name", "created")
    filter_horizontal = ("products",)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
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
