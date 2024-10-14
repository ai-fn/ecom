from typing import Any
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.related import ForeignKey
from django.forms.models import ModelChoiceField
from django.http import HttpRequest

from api.mixins import ActiveAdminMixin
from shop.models import (
    Brand,
    Category,
    Characteristic,
    CharacteristicValue,
    FavoriteProduct,
    OpenGraphMeta,
    Page,
    Price,
    Product,
    ProductFile,
    ProductGroup,
    ProductImage,
    Promo,
    Review,
    SearchHistory,
    Setting,
    FooterItem,
    Banner,
    MainPageCategoryBarItem,
    ProductFrequenlyBoughtTogether,
    SideBarMenuItem,
    ItemSet,
    ItemSetElement,
    Slider,
)
from mptt.admin import DraggableMPTTAdmin


class CharacteristicInline(admin.TabularInline):
    model = Characteristic.categories.through
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
    prepopulated_fields = {"slug": ("name",)}
    mptt_level_indent = 30

    def get_form(self, request, obj=None, **kwargs):
        form = super(CustomMPTTModelAdmin, self).get_form(request, obj, **kwargs)
        if obj and obj.parent:  # Проверяем, есть ли у категории родитель
            form.base_fields["image"].disabled = True
        else:
            form.base_fields["image"].disabled = False
        return form


@admin.register(Category)
class CategoryAdmin(ActiveAdminMixin, CustomMPTTModelAdmin):
    inlines = [CharacteristicInline]


@admin.register(Brand)
class BrandAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "order",
    )
    search_fields = (
        "name",
        "slug",
        "order",
    )
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "article",
        "id",
        "title",
        "brand",
        "category",
        "is_popular",
        "is_new",
        'priority',
        "is_active",
    )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title",)
    list_filter = (
        "category",
        "brand",
        "is_popular",
        "in_stock",
        "is_new",
        "is_active",
    )
    inlines = [
        PromoInline,
        CharacteristicValueInline,
        ProductGroupInline,
    ] 
    filter_horizontal = (
        "additional_categories",
        "similar_products",
        "unavailable_in", 
    ) 


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = ("id", "user", "product", "created_at", "updated_at")
    search_fields = ("user__username", "product__title")
    list_filter = ("created_at", "updated_at")


@admin.register(ProductFile)
class ProductFileAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'product',
    )
    list_filter = (
        "product",
    )
    search_fields = (
        'name',
        'product__title',
    )


@admin.register(ProductGroup)
class ProductGroupAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "characteristic",
    )
    search_fields = ("name", "products__title")
    filter_horizontal = ("products",)


@admin.register(ProductFrequenlyBoughtTogether)
class ProductFrequenlyBoughtTogetherAdmin(ActiveAdminMixin, admin.ModelAdmin):
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
class ProductImageAdmin(ActiveAdminMixin, admin.ModelAdmin):
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
class ReviewAdmin(ActiveAdminMixin, admin.ModelAdmin):
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
class CharacteristicAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "for_filtering",
    )
    list_filter = ("categories", "for_filtering",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = (
        "name",
        "slug",
        "categories__name",
        "categories__slug",
    )
    filter_horizontal = ("categories",)


@admin.register(CharacteristicValue)
class CharacteristicValueAdmin(ActiveAdminMixin, admin.ModelAdmin):
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
class PriceAdmin(ActiveAdminMixin, admin.ModelAdmin):
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
class SettingAdmin(ActiveAdminMixin, admin.ModelAdmin):
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
class PromoAdmin(ActiveAdminMixin, admin.ModelAdmin):
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
    filter_horizontal = (
        "categories", "products", "cities",
    )


@admin.register(FooterItem)
class FooterItemAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "column",
        "title",
        "link",
        "order",
    )
    search_fields = ("title",)


@admin.register(Banner)
class BannerAdmin(ActiveAdminMixin, admin.ModelAdmin):
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


@admin.register(Slider)
class SliderAdmin(ActiveAdminMixin, admin.ModelAdmin):
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
class MainPageCategoryBarItemAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "link",
        "order",
        "text",
    )

    search_fields = ("text", "link")


@admin.register(SideBarMenuItem)
class SideBarMenuItemAdmin(ActiveAdminMixin, admin.ModelAdmin):

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
class OpenGraphMetaAdmin(ActiveAdminMixin, admin.ModelAdmin):

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
    )
    list_filter = ("locale",)


@admin.register(Page)
class PageAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "description",
    )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = (
        "title",
        "description",
    )

@admin.register(SearchHistory)
class SearchHistoryAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "user",
    )
    search_fields = (
        "title",
    )
    ordering = ("created_at", "title")
    list_filter = ("user",)


class ContentTypeFilter(admin.SimpleListFilter):
    title = 'content type'
    parameter_name = 'content_type'

    def lookups(self, request, model_admin):
        allowed_content_types = ContentType.objects.filter(
            model__in=model_admin.model.objects.values_list(
                "item_set__itemset_type",
                flat=True,
            )
        )
        return [(ct.id, ct.model) for ct in allowed_content_types]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type__id__exact=self.value())
        return queryset


@admin.register(ItemSet)
class ItemSetAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "description",
        "itemset_type",
        "order",
    )
    list_filter = (
        "itemset_type",
    )

@admin.register(ItemSetElement)
class ItemSetElementAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "content_type",
        "order",
        "item_set",
    )
    list_filter = (
        ContentTypeFilter,
        "item_set",
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "content_type":
            kwargs["queryset"] = ContentType.objects.filter(model__in=ItemSet.ItemSetType.values)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
