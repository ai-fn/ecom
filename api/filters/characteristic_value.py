from shop.models import CharacteristicValue
from django_filters import rest_framework as filters


class CharacteristicValueFilters(filters.FilterSet):
    """
    Фильтр-сет для модели CharacteristicValue.

    Позволяет фильтровать записи модели по различным полям, включая уникальность значений.
    """


    unique = filters.BooleanFilter(method="unique_filter")

    class Meta:
        model = CharacteristicValue
        fields = ["characteristic", "product", "value", "slug", "created_at", "updated_at", "unique"]
    
    def unique_filter(self, queryset, name, value):
        """
        Метод фильтрации уникальных значений на основе поля `slug`.

        :param queryset: QuerySet, к которому применяется фильтр.
        :type queryset: QuerySet
        :param name: Имя фильтра.
        :type name: str
        :param value: Значение фильтра (True для включения уникальных записей).
        :type value: bool
        :return: Отфильтрованный QuerySet.
        :rtype: QuerySet
        """

        if value:
            return queryset.order_by("slug").distinct("slug")
        
        return queryset
