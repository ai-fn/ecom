from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from shop.models import (
    Category,
    Characteristic,
    CharacteristicValue,
    Price,
    Product,
    Review,
    Setting,
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


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ("get_key", "type", "get_value")
    fields = (
        "predefined_key",
        "custom_key",
        "type",
        "value_string",
        "value_boolean",
        "value_number",
    )
    list_filter = ("type",)
    search_fields = ("predefined_key", "custom_key")

    def get_form(self, request, obj=None, **kwargs):
        form = super(SettingAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            if obj.predefined_key:
                form.base_fields["custom_key"].disabled = True
            elif obj.custom_key:
                form.base_fields["predefined_key"].disabled = True
        else:
            form.base_fields["predefined_key"].disabled = False
            form.base_fields["custom_key"].disabled = False
        return form
