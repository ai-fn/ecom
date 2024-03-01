from shop.models import  Category, Brand, Product
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils.text import slugify


@receiver(pre_save, sender=Category)
def set_category_order(sender, instance, **kwargs):
    if not instance.order:
        instance.order = get_order(sender)

@receiver(pre_save, sender=Brand)
def set_brand_order(sender, instance, **kwargs):
    if not instance.order:
        instance.order = get_order(sender)

@receiver(pre_save, sender=Product)
def set_product_slug(sender, instance, **kwargs):
    if not instance.id:
        id = sender.objects.last().id + 1 if sender.objects.last() else 1
    else:
        id = instance.id
    instance.slug = slugify(instance.title) + "-%s" % id
    print(instance.slug, instance.title)


def get_order(sender):
    last_obj = sender.objects.order_by("order").last()
    return last_obj.order + 1 if last_obj else 1
