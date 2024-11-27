from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.fields import empty
from django.db.models import Avg


class RatingMixin(ModelSerializer):
    """
    Mixin для добавления полей `rating` и `reviews_count` в сериализатор.

    `rating` - средний рейтинг объекта, основанный на связанных отзывах.
    `reviews_count` - количество отзывов для объекта.
    """

    reviews_count: SerializerMethodField = SerializerMethodField()
    rating: SerializerMethodField = SerializerMethodField()

    class Meta:
        abstract = True

    def __init__(self, instance=None, data=empty, **kwargs):
        """
        Инициализация миксина.

        :param instance: Экземпляр модели.
        :param data: Входные данные для сериализатора.
        :param kwargs: Дополнительные именованные аргументы.
        """
        super().__init__(instance, data, **kwargs)
        for field_name in ("rating", "reviews_count"):
            self.fields[field_name] = SerializerMethodField()

    def get_rating(self, obj) -> float:
        """
        Вычисляет средний рейтинг объекта.

        :param obj: Объект модели, для которого вычисляется рейтинг.
        :return: Средний рейтинг объекта, округленный до одной десятичной.
        :rtype: float
        """
        value = obj.reviews.aggregate(average_rating=Avg('rating'))['average_rating'] or 0.0
        return round(value, 1)

    def get_reviews_count(self, obj) -> int:
        """
        Вычисляет количество отзывов для объекта.

        :param obj: Объект модели, для которого вычисляется количество отзывов.
        :return: Количество отзывов для объекта.
        :rtype: int
        """
        return obj.reviews.count()
