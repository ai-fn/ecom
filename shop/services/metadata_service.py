from typing import Any, Dict, Iterable, Literal
from django.contrib.contenttypes.models import ContentType

from pymorphy2 import MorphAnalyzer

from shop.models import OpenGraphMeta
from account.models import City, CityGroup

_morph = MorphAnalyzer()


def _inflect_phrase(phrase: str, case: str) -> str:
    """
    Склоняет фразу в заданный падеж.

    :param phrase: Фраза для склонения.
    :param case: Падеж ("nomn", "gent", "datv", "accs", "ablt", "loct").
    :return: Склоненная фраза.
    """
    words = phrase.split()
    inflected_words = []

    for idx, word in enumerate(words):
        parsed = _morph.parse(word)[0]
        inflected_word = parsed.inflect({case})

        word = inflected_word.word if inflected_word else word
        if idx == 0:
            word = word.title()

        inflected_words.append(word)

    return " ".join(inflected_words)


class MetaDataService:
    """
    Сервис для формирования мета-тегов и обработки данных для OpenGraph.
    """

    @staticmethod
    def get_obj_by_slug(slug: str, content_type: str) -> OpenGraphMeta:
        """
        Получение объекта OpenGraphMeta по слагу.

        :param slug: Слаг объекта.
        :param content_type: Тип контента (имя модели).
        :return: Объект OpenGraphMeta.
        """
        tp = ContentType.objects.get(model=content_type)
        model = tp.model_class()
        instance = model.objects.get(slug=slug)
        kwargs = dict(object_id=instance.pk, content_type=content_type.upper())

        meta = OpenGraphMeta.objects.filter(**kwargs).first()
        if not meta:
            meta = OpenGraphMeta(pk=999, **kwargs)

        return meta

    @staticmethod
    def _correct_ending(number: int) -> str:
        """
        Возвращает слово с правильным окончанием в зависимости от числа.

        :param number: Число.
        :return: Слово с правильным окончанием.
        """
        if number % 10 == 1 and number % 100 != 11:
            return f"{number} товар"
        elif number % 10 in [2, 3, 4] and (number % 100 not in [12, 13, 14]):
            return f"{number} товара"
        else:
            return f"{number} товаров"

    @classmethod
    def get_formatted_meta_tag_by_instance(
        cls,
        meta_obj: OpenGraphMeta,
        instance,
        fields: Iterable[Literal["title", "description", "keywords"]],
        city_domain: str = None,
    ) -> Dict[str, str]:
        """
        Формирует мета-теги на основе шаблона OpenGraphMeta и данных экземпляра.

        :param meta_obj: Объект OpenGraphMeta.
        :param instance: Экземпляр модели.
        :param fields: Поля мета-тегов для формирования.
        :param city_domain: Домен города.
        :return: Словарь сформированных мета-тегов.
        """
        city = cls._get_city(city_domain)
        city_group_name = cls._get_city_group_name(city)

        values = cls._get_meta_values(meta_obj, fields)
        if not values:
            values = cls._get_default_meta_values(meta_obj, fields)

        object_name = cls._get_object_name(instance)
        price_value, products_count = cls._get_price_and_count(instance, city_group_name)

        kwargs = cls._prepare_kwargs(
            object_name, price_value, city, city_group_name, products_count
        )
        result = cls._format_values(values, kwargs)

        return result

    @classmethod
    def _get_city(cls, city_domain: str) -> City:
        """
        Возвращает объект City по домену или город по умолчанию.

        :param city_domain: Домен города.
        :return: Объект City.
        """
        return City.objects.filter(domain=city_domain).first() or City.get_default_city()

    @classmethod
    def _get_city_group_name(cls, city: City) -> str:
        """
        Возвращает название группы города.

        :param city: Объект City.
        :return: Название группы города.
        """
        return city.city_group.name if city.city_group else CityGroup.get_default_city_group().name

    @classmethod
    def _get_meta_values(
        cls, meta_obj: OpenGraphMeta, fields: Iterable[str]
    ) -> Dict[str, Any]:
        """
        Возвращает значения мета-тегов из объекта OpenGraphMeta.

        :param meta_obj: Объект OpenGraphMeta.
        :param fields: Поля для получения.
        :return: Словарь значений мета-тегов.
        """
        return {
            field: getattr(meta_obj, field, None)
            for field in fields
            if getattr(meta_obj, field, None)
        }

    @classmethod
    def _get_default_meta_values(
        cls, meta_obj: OpenGraphMeta, fields: Iterable[str]
    ) -> Dict[str, Any]:
        """
        Возвращает значения мета-тегов из шаблона по умолчанию.

        :param meta_obj: Объект OpenGraphMeta.
        :param fields: Поля для получения.
        :return: Словарь значений мета-тегов.
        """
        default_meta_obj = meta_obj.get_default_template()
        if default_meta_obj is None:
            raise FileNotFoundError(
                f"Шаблон для объекта '{meta_obj.get_content_object()}' не найден."
            )

        return {
            field: getattr(default_meta_obj, field, None)
            for field in fields
            if getattr(default_meta_obj, field, None)
        }

    @classmethod
    def _get_object_name(cls, instance) -> str:
        """
        Возвращает название объекта.

        :param instance: Экземпляр модели.
        :return: Название объекта.
        """
        return getattr(instance, "title", None) or getattr(instance, "name", None)

    @classmethod
    def _get_price_and_count(cls, instance, city_group_name: str) -> tuple[Any, int]:
        """
        Получает минимальную цену и количество товаров для объекта.

        :param instance: Экземпляр модели.
        :param city_group_name: Название группы городов.
        :return: Кортеж (минимальная цена, количество товаров).
        """
        if instance._meta.model_name == "product":
            price_value = (
                instance.prices.filter(city_group__name=city_group_name)
                .values_list("price", flat=True)
                .first()
            )
            products_count = instance.category.products.count()
        elif instance._meta.model_name == "category":
            ctgs = (
                instance.get_descendants(include_self=True)
                .filter(
                    is_visible=True,
                    is_active=True,
                    products__isnull=False,
                    products__prices__city_group__name=city_group_name,
                )
                .distinct()
            )

            price_value = (
                ctgs.prefetch_related("products__prices")
                .order_by("products__prices__price")
                .values_list("products__prices__price", flat=True)
                .first()
            )
            products_count = sum(ctg.products.count() for ctg in ctgs)
        else:
            price_value, products_count = None, 0

        return price_value, products_count

    @classmethod
    def _prepare_kwargs(
        cls,
        object_name: str,
        price_value: Any,
        city: City,
        city_group_name: str,
        products_count: int,
    ) -> Dict[str, Any]:
        """
        Подготавливает параметры для форматирования мета-тегов.

        :param object_name: Название объекта.
        :param price_value: Цена.
        :param city: Объект City.
        :param city_group_name: Название группы города.
        :param products_count: Количество товаров.
        :return: Словарь параметров.
        """
        count_str = cls._correct_ending(products_count)
        price = int(price_value) if price_value is not None else "--"

        kwargs = {
            "object_name": object_name,
            "price": price,
            "city_group": city_group_name,
            "count": count_str,
        }
        cases = ("nomn", "gent", "datv", "accs", "ablt", "loct")
        for case in cases:
            cg_name = getattr(city.city_group, "name", "")
            kwargs[f"c_{case}"] = _inflect_phrase(city.name, case)
            kwargs[f"cg_{case}"] = _inflect_phrase(cg_name, case)

        return kwargs

    @classmethod
    def _format_values(
        cls, values: Dict[str, Any], kwargs: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Форматирует значения мета-тегов с использованием параметров.

        :param values: Словарь значений мета-тегов.
        :param kwargs: Словарь параметров для форматирования.
        :return: Словарь отформатированных мета-тегов.
        """
        return {field: value.format(**kwargs) for field, value in values.items()}
