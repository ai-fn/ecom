from functools import cached_property
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from django.core.paginator import Page, Paginator as DjangoPaginator


class CustomPaginator(DjangoPaginator):
    """
    Кастомный пагинатор, позволяющий использовать произвольное количество объектов
    и переопределять подсчет количества записей через `count`.
    """

    def __init__(self, *args, count: int = None, **kwargs) -> None:
        """
        Инициализация кастомного пагинатора.

        :param count: Общее количество объектов, если известно заранее.
        :type count: int, optional
        """
        super().__init__(*args, **kwargs)
        if count is not None:
            self._count = count

    @cached_property
    def count(self) -> int:
        """
        Возвращает общее количество объектов через `_count`, если он установлен,
        иначе вызывает стандартный подсчет.

        :return: Общее количество объектов.
        :rtype: int
        """
        if hasattr(self, "_count"):
            return self._count
        return super().count

    def _get_page(self, *args, **kwargs) -> Page:
        """
        Возвращает экземпляр страницы.

        :return: Экземпляр страницы.
        :rtype: Page
        """
        return Page(*args, **kwargs)

    def page(self, number: int) -> Page:
        """
        Возвращает объект страницы для указанного номера страницы.

        :param number: Номер страницы (1-based).
        :type number: int
        :return: Объект страницы.
        :rtype: Page
        :raises InvalidPage: Если номер страницы невалиден.
        """
        number = self.validate_number(number)
        if len(self.object_list) > self.per_page:
            bottom = (number - 1) * self.per_page
        else:
            bottom = 0

        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count

        return self._get_page(self.object_list[bottom:top], number, self)


class CustomProductPagination(PageNumberPagination):
    """
    Кастомная пагинация для продуктов, использующая `CustomPaginator`.
    """

    django_paginator_class = CustomPaginator

    def paginate_queryset(
        self, queryset, request, view=None, count: int = None
    ) -> list:
        """
        Пагинирует QuerySet.

        :param queryset: QuerySet для пагинации.
        :param request: HTTP-запрос.
        :param view: View, связанный с запросом.
        :param count: Общее количество объектов, если известно заранее.
        :type count: int, optional
        :return: Список объектов текущей страницы.
        :rtype: list
        :raises NotFound: Если номер страницы невалиден.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size, count=count)
        page_number = self.get_page_number(request, paginator)
        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        """
        Возвращает пагинированный ответ.

        :param data: Данные текущей страницы.
        :return: Пагинированный ответ.
        """
        return super().get_paginated_response(data)
