from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import OpenApiExample, extend_schema

from api.serializers import SideBarMenuItemSerializer
from shop.models import SideBarMenuItem
from api.permissions import ReadOnlyOrAdminPermission


@extend_schema(
    tags=["Shop"]
)
class SideBarMenuItemViewSet(ModelViewSet):

    queryset = SideBarMenuItem.objects.all()
    serializer_class = SideBarMenuItemSerializer
    permission_classes = (ReadOnlyOrAdminPermission, )

    @extend_schema(
        description="Получение списка элементов бокового меню",
        summary="Получение списка элементов бокового меню",
        examples=[
            OpenApiExample(
                name="Пример ответа",
                description="Пример ответа",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "order": 1,
                        "title": "Dummy title",
                        "link": "/katalog/"
                    }
                ]
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        description="Получение элемента бокового меню по уникальному идентификатору",
        summary="Получение элемента бокового меню по уникальному идентификатору",
        examples=[
            OpenApiExample(
                name="Пример ответа",
                description="Пример ответа",
                response_only=True,
                value={
                        "id": 1,
                        "order": 1,
                        "title": "Dummy title",
                        "link": "/katalog/"
                    }
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        description="Создание элемента бокового меню",
        summary="Создание элемента бокового меню",
        examples=[
            OpenApiExample(
                name="Пример запроса",
                description="Пример запроса",
                request_only=True,
                value={
                        "order": 1,
                        "title": "Dummy title",
                        "link": "/katalog/"
                    }
            ),
            OpenApiExample(
                name="Пример ответа",
                description="Пример ответа",
                response_only=True,
                value={
                        "id": 1,
                        "order": 1,
                        "title": "Dummy title",
                        "link": "/katalog/"
                    }
            )
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        description="Обновление элемента бокового меню",
        summary="Обновление элемента бокового меню",
        examples=[
            OpenApiExample(
                name="Пример запроса",
                description="Пример запроса",
                request_only=True,
                value={
                        "order": 1,
                        "title": "Dummy title",
                        "link": "/katalog/"
                    }
            ),
            OpenApiExample(
                name="Пример ответа",
                description="Пример ответа",
                response_only=True,
                value={
                        "id": 1,
                        "order": 1,
                        "title": "Dummy title",
                        "link": "/katalog/"
                    }
            )
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        description="Частичное обновление элемента бокового меню",
        summary="Частичное обновление элемента бокового меню",
        examples=[
            OpenApiExample(
                name="Пример запроса",
                description="Пример запроса",
                request_only=True,
                value={
                        "title": "Updated Dummy title",
                    }
            ),
            OpenApiExample(
                name="Пример ответа",
                description="Пример ответа",
                response_only=True,
                value={
                        "id": 1,
                        "order": 1,
                        "title": "Updated Dummy title",
                        "link": "/katalog/"
                    }
            )
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        description="Удаление элемента бокового меню",
        summary="Удаление элемента бокового меню",
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
