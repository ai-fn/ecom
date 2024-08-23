from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework import status


class IntegrityErrorHandlingMixin:
    def handle_integrity_error(self, exc):
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except IntegrityError as e:
            return self.handle_integrity_error(e)
