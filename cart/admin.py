from django.contrib import admin

from .models import CartItem, Order, ProductsInOrder, PickupPoint
from api.mixins import ActiveAdminMixin


class ProductsInOrderInline(admin.TabularInline):
    model = ProductsInOrder

    verbose_name = "Заказанный товар"
    verbose_name_plural = "Заказанные товары"


@admin.register(Order)
class OrderAdmin(ActiveAdminMixin, admin.ModelAdmin):
    ordering = ("created_at",)
    list_display = (
        "customer",
        "quantity",
        "created_at",
    )
    list_filter = ("status",)

    inlines = (ProductsInOrderInline,)

    def quantity(self, obj):
        return ProductsInOrder.objects.filter(order=obj).count()

    quantity.short_description = "Количество позиций"


@admin.register(PickupPoint)
class PickupPointAdmin(ActiveAdminMixin, admin.ModelAdmin):
    ordering = ("created_at",)
    list_display = (
        "id",
        "address",
        "coord_x",
        "coord_y",
        "created_at",
        "is_active",
    )
    list_filter = ("is_active",)


@admin.register(CartItem)
class CartAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "customer",
        "product",
        "quantity",
    )
    