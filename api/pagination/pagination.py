from functools import cached_property
from rest_framework.pagination import PageNumberPagination

from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from django.core.paginator import Page, Paginator as DjangoPaginator


class CustomPaginator(DjangoPaginator):

    def __init__(self, *args, count: int = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if count is not None:
            self._count = count

    @cached_property
    def count(self):
        """Return the total number of objects, across all pages."""
        if hasattr(self, "_count"):
            return self._count
        
        return super().count

    def _get_page(self, *args, **kwargs):
        """
        Return an instance of a single page.

        This hook can be used by subclasses to use an alternative to the
        standard :cls:`Page` object.
        """
        return Page(*args, **kwargs)

    def page(self, number):
        """Return a Page object for the given 1-based page number."""
        number = self.validate_number(number)
        if len(self.object_list) > self.per_page:
            bottom = (number - 1) * self.per_page
        else:
            bottom = 0

        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return self._get_page(self.object_list[bottom:top], number, self)

    def validate_number(self, number: int | float | str | None) -> int:
        return super().validate_number(number)

class CustomProductPagination(PageNumberPagination):
    django_paginator_class = CustomPaginator

    def paginate_queryset(self, queryset, request, view=None, count=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
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
        return super().get_paginated_response(data)
