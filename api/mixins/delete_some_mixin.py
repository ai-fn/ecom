from typing import List
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class DeleteSomeMixin:
    @action(detail=False, methods=["post"], url_path="delete-some")
    def delete_some(self, request, *args, **kwargs):
        ids = request.data.get("ids")
        if ids is None:
            return Response({"detail": "'ids' field is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(ids, List):
            return Response({"detail": "'ids' field must be a list."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().filter(pk__in=ids)
        if queryset.exists():
            queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
