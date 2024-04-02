from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from shop.signals import set_brand_order, set_category_order, set_product_slug
from django.core.signals import setting_changed

from shop.models import (
    Brand,
    Category,
    CategoryMetaData,
    Characteristic,
    CharacteristicValue,
    Price,
    Product,
    ProductImage,
    Promo,
    Review,
    Setting,
    FooterItem,
    FooterSettings,
    MainPageSliderImage,
    MainPageCategoryBarItem,
    ProductFrequenlyBoughtTogether,
)
from mptt.admin import DraggableMPTTAdmin


def ready():
    setting_changed.connect(set_brand_order)
    setting_changed.connect(set_category_order)
    setting_changed.connect(set_product_slug)


class CategoryMetaDataInline(admin.TabularInline):
    model = CategoryMetaData
    extra = 1  # Количество пустых форм для новых записей


class CharacteristicInline(admin.TabularInline):
    model = Characteristic
    extra = 1


class CharacteristicValueInline(admin.TabularInline):
    model = CharacteristicValue
    extra = 1


class PromoInline(admin.TabularInline):
    model = Promo
    extra = 1


class CustomMPTTModelAdmin(DraggableMPTTAdmin):
    inlines = [CategoryMetaDataInline, CharacteristicInline]
    prepopulated_fields = {"slug": ("name",)}
    mptt_level_indent = 30

    def get_form(self, request, obj=None, **kwargs):
        form = super(CustomMPTTModelAdmin, self).get_form(request, obj, **kwargs)
        if obj and obj.parent:  # Проверяем, есть ли у категории родитель
            form.base_fields["image"].disabled = True
        else:
            form.base_fields["image"].disabled = False
        return form


admin.site.register(Category, CustomMPTTModelAdmin)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
    )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title",)
    list_filter = (
        "category",
        "brand",
    )
    inlines = [PromoInline, CharacteristicValueInline]


@admin.register(ProductFrequenlyBoughtTogether)
class ProductFrequenlyBoughtTogetherAdmin(admin.ModelAdmin):
    list_display = (
        "product_from",
        "product_to",
        "purchase_count"
    )
    list_filter = (
        "product_from",
        "product_to"
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = [
        "product",
    ]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reviewer_name",
        "product",
        "rating",
    )

    list_filter = ("product",)

    def reviewer_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


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


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "product",
        "image",
        "is_active",
        "active_to",
    )
    list_filter = (
        "category",
        "cities",
        "is_active",
        "active_to",
    )


@admin.register(FooterItem)
class FooterItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "link",
        "order",
        "footer_settings",
    )
    list_filter = ("footer_settings",)
    search_fields = ("title",)


@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "max_footer_items",
    )


@admin.register(MainPageSliderImage)
class MainPageSliderImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image_text",
        "button_text",
        "link",
        "order",
        "image",
    )
    search_fields = ("image_text", "link", "button_text")


@admin.register(MainPageCategoryBarItem)
class MainPageCategoryBarItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "link",
        "order",
        "text",
    )

    search_fields = ("text", "link")
