from typing import Iterable, Literal
from django.contrib.contenttypes.models import ContentType

from account.models import City, CityGroup
from shop.models import OpenGraphMeta, Price


class MetaDataService:

    @staticmethod
    def get_obj_by_slug(slug: str, content_type: str) -> OpenGraphMeta:
        """
        Получение метаданных по слагу
        """
        tp = ContentType.objects.get(model=content_type)
        model = tp.model_class()
        if model._meta.model_name == "product":
            product = model.objects.get(slug=slug)
            instance = product.category
            tp = ContentType.objects.get_for_model(instance._meta.model)
        else:
            instance = model.objects.get(slug=slug)

        meta = OpenGraphMeta.objects.get(object_id=instance.pk, content_type=tp)
        return meta

    @staticmethod
    def get_formatted_meta_tag_by_instance(
        meta_obj: OpenGraphMeta,
        instance,
        fields: Iterable[Literal["title", "description", "keywords"]],
        city_domain: str = None,
    ):
        try:
            if not city_domain:
                raise City.DoesNotExist
            else:
                city = City.objects.get(domain=city_domain)
        except City.DoesNotExist:
            city = City.get_default_city()

        if city.city_group is not None:
            city_group_name = city.city_group.name
        else:
            city_group_name = CityGroup.get_default_city_group().name

        result = {}
        products_count = 0
        for field in fields:
            price = None
            value: str = getattr(meta_obj, field)
            object_name = getattr(instance, "title", None) or getattr(
                instance, "name", None
            )
            if instance._meta.model_name == "product":
                price_value = (
                    instance.prices.filter(city_group__name=city_group_name)
                    .values_list("price", flat=True)
                    .first()
                )
                price = int(price_value) if price_value is not None else "--"
                products_count = instance.category.products.count() 
            elif instance._meta.model_name == "category":
                price_value = (
                    instance.products.prefetch_related("prices")
                    .order_by("prices__price")
                    .values_list("prices__price", flat=True)
                    .first()
                )
                price = (
                    f"от {int(price_value)}" if price_value is not None else "--"
                )
                products_count = instance.products.count()

            result[field] = value.format(
                object_name=object_name,
                price=price,
                city_group=city_group_name,
                nominative_case=city.nominative_case,
                genitive_case=city.genitive_case,
                dative_case=city.dative_case,
                accusative_case=city.accusative_case,
                instrumental_case=city.instrumental_case,
                prepositional_case=city.prepositional_case,
                count=products_count,
            )

        return result
