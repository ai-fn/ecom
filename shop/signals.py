from shop.models import Category, Brand, FooterItem, Product
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.utils.text import slugify
from unidecode import unidecode


@receiver(pre_save, sender=Category)
def set_category_order(sender, instance, **kwargs):
    if not instance.order:
        instance.order = get_order(sender)

@receiver(pre_save, sender=FooterItem)
def set_category_order(sender, instance, **kwargs):
    if not instance.order:
        instance.order = get_order(sender)

@receiver(pre_save, sender=Brand)
def set_brand_order(sender, instance, **kwargs):
    if not instance.order:
        instance.order = get_order(sender)


@receiver(post_save, sender=Product)
def set_product_slug(sender, created, instance, **kwargs):
    if created:
        instance.slug = slugify(unidecode(instance.title)) + f"-{instance.id}"
        instance.save()


@receiver(post_save, sender=Category)
def set_category_slug(sender, created, instance, **kwargs):
    if created:
        instance.slug = slugify(unidecode(instance.name)) + f"-{instance.id}"
        instance.save()

@receiver(post_save, sender=Brand)
def set_category_slug(sender, created, instance, **kwargs):
    if created:
        instance.slug = slugify(unidecode(instance.name)) + f"-{instance.id}"
        instance.save()

def get_order(sender):
    last_obj = sender.objects.order_by("order").last()
    return last_obj.order + 1 if last_obj else 1
