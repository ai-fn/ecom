from django.contrib import admin

from .models import CartItem, Order, ProductsInOrder


class ProductsInOrderInline(admin.TabularInline):
    model = ProductsInOrder

    verbose_name = "Заказанный товар"
    verbose_name_plural = "Заказанные товары"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ordering = ("created_at",)
    list_display = (
        "customer",
        "quantity",
        "created_at",
    )

    inlines = (ProductsInOrderInline,)

    def quantity(self, obj):
        return ProductsInOrder.objects.filter(order=obj).count()

    quantity.short_description = "Количество позиций"


@admin.register(CartItem)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "product",
        "quantity",
    )
    