from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework import status


class IntegrityErrorHandlingMixin:
    def handle_integrity_error(self, exc):
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            return self.handle_integrity_error(e)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError as e:
            return self.handle_integrity_error(e)

    def partial_update(self, request, *args, **kwargs):
        try:
            return super().partial_update(request, *args, **kwargs)
        except IntegrityError as e:
            return self.handle_integrity_error(e)
