from typing import List, Any
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class DeleteSomeMixin:
    """
    Миксин для добавления возможности массового удаления объектов.

    Добавляет маршрут `/delete-some/` для удаления объектов по переданному списку идентификаторов.
    """

    @action(detail=False, methods=["post"], url_path="delete-some")
    def delete_some(self, request, *args: Any, **kwargs: Any) -> Response:
        """
        Удаляет объекты, указанные в списке идентификаторов.

        :param request: HTTP-запрос.
        :type request: HttpRequest
        :param args: Дополнительные позиционные аргументы.
        :param kwargs: Дополнительные именованные аргументы.
        :return: HTTP-ответ с результатом удаления.
        :rtype: Response
        """
        ids = request.data.get("ids")
        if ids is None:
            return Response(
                {"detail": "'ids' field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(ids, list):
            return Response(
                {"detail": "'ids' field must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(pk__in=ids)
        if queryset.exists():
            queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
