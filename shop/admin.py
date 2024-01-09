from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from shop.models import (
    Category,
    Characteristic,
    CharacteristicValue,
    Price,
    Product,
    Review,
)
from mptt.admin import DraggableMPTTAdmin


class CustomMPTTModelAdmin(DraggableMPTTAdmin):
    mptt_level_indent = 30


admin.site.register(Category, CustomMPTTModelAdmin)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
    )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title",)
    list_filter = ("category",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "product",
        "rating",
    )


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
    )
    list_filter = ("category",)


@admin.register(CharacteristicValue)
class CharacteristicValueAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "characteristic",
        "value",
    )


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "city",
        "price",
    )
