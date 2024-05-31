from django.contrib import admin
from django.core.signals import setting_changed

from shop.models import (
    Brand,
    Category,
    CategoryMetaData,
    Characteristic,
    CharacteristicValue,
    ImageMetaData,
    OpenGraphMeta,
    Page,
    Price,
    Product,
    ProductGroup,
    ProductImage,
    Promo,
    Review,
    Setting,
    FooterItem,
    MainPageSliderImage,
    MainPageCategoryBarItem,
    ProductFrequenlyBoughtTogether,
    SideBarMenuItem,
)
from mptt.admin import DraggableMPTTAdmin


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
    model = Promo.products.through
    extra = 1


class ProductGroupInline(admin.TabularInline):
    model = ProductGroup.products.through
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
        "order",
        "id",
        "name",
    )
    search_fields = (
        "name",
        "slug",
        "order",
    )
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "article",
        "id",
        "title",
        "category",
        "is_popular",
        "is_new",
    )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title",)
    list_filter = (
        "category",
        "brand",
        "is_popular",
        "in_stock",
        "is_new",
    )
    inlines = [PromoInline, CharacteristicValueInline, ProductGroupInline]


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "characteristic",
    )
    search_fields = ("name", "products__title")


@admin.register(ProductFrequenlyBoughtTogether)
class ProductFrequenlyBoughtTogetherAdmin(admin.ModelAdmin):
    list_display = ("product_from", "product_to", "purchase_count")
    list_filter = ("product_from", "product_to")
    search_fields = (
        "product_from__title",
        "product_to__title",
        "product_from__slug",
        "product_to__slug",
        "purchase_count",
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "name",
    ]
    search_fields = (
        "product__title",
        "name",
    )
    list_filter = ("product",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reviewer_name",
        "product",
        "rating",
    )
    search_fields = (
        "user__username",
        "user__phone",
        "user__middle_name",
        "user__first_name",
        "user__last_name",
        "product__title",
        "product__slug",
        "rating",
    )

    list_filter = (
        "product",
        "user",
    )

    def reviewer_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "for_filtering",
    )
    list_filter = ("category", "for_filtering",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = (
        "name",
        "slug",
        "category__name",
        "category__slug",
    )


@admin.register(CharacteristicValue)
class CharacteristicValueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "characteristic",
        "value",
    )
    prepopulated_fields = {"slug": ("value",)}
    search_fields = (
        "product__title",
        "characteristic__name",
        "value",
    )
    list_filter = (
        "product",
        "characteristic",
    )


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "city_group",
        "price",
        "old_price",
    )
    search_fields = ("product__title",)
    list_filter = (
        "product",
        "city_group",
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
        "image",
        "is_active",
        "active_to",
    )
    list_filter = (
        "categories",
        "cities",
        "is_active",
        "active_to",
    )
    search_fields = (
        "name",
        "cities__name",
        "categories__name",
        "categories__slug",
    )


@admin.register(FooterItem)
class FooterItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "column",
        "title",
        "link",
        "order",
    )
    search_fields = ("title",)


@admin.register(MainPageSliderImage)
class MainPageSliderImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "description",
        "button_text",
        "link",
        "order",
        "image",
    )
    search_fields = ("title", "description", "link", "button_text")


@admin.register(MainPageCategoryBarItem)
class MainPageCategoryBarItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "link",
        "order",
        "text",
    )

    search_fields = ("text", "link")


@admin.register(SideBarMenuItem)
class SideBarMenuItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "link",
    )
    search_fields = (
        "title",
        "link",
    )


@admin.register(OpenGraphMeta)
class OpenGraphMetaAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "url",
    )
    search_fields = (
        "title",
        "description",
        "url",
        "site_name",
        "locale",
        "content_type",
    )
    list_filter = ("locale",)


@admin.register(ImageMetaData)
class ImageMetaDataAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image",
        "width",
        "height",
    )
    search_fields = (
        "image",
        "width",
        "height",
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
    )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = (
        "title",
        "description",
    )
