from django.db.models import QuerySet


class ActiveQuerysetMixin:
    """
    Mixin для фильтрации QuerySet на основе поля `is_active`.

    Если пользователь является сотрудником (staff), возвращается полный QuerySet.
    Для остальных пользователей возвращается только активные записи.
    """

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        """
        Получает отфильтрованный QuerySet.

        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Отфильтрованный QuerySet.
        :rtype: QuerySet
        """
        queryset = super().get_queryset(*args, **kwargs)
        if self.request.user.is_staff:
            return queryset

        return queryset.filter(is_active=True)
