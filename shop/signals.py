from shop.models import  Category, Brand
from django.dispatch import receiver
from django.db.models.signals import pre_save


@receiver(pre_save, sender=Category)
def set_category_order(sender, instance, **kwargs):
    if not instance.order:
        instance.order = get_order(sender)

@receiver(pre_save, sender=Brand)
def set_brand_order(sender, instance, **kwargs):
    if not instance.order:
        instance.order = get_order(sender)

def get_order(sender):
    last_obj = sender.objects.order_by("order").last()
    return last_obj.order + 1 if last_obj else 1
