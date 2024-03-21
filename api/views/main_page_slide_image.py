from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample

from api.permissions import ReadOnlyOrAdminPermission
from shop.models import MainPageSliderImage
from api.serializers import MainPageSliderImageSerializer


@extend_schema(
    tags=["Settings"]
)
class MainPageSliderImageViewSet(viewsets.ModelViewSet):
    queryset = MainPageSliderImage.objects.all()
    serializer_class = MainPageSliderImageSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    @extend_schema(
        description="This endpoint retrieves a list of all main page slider images.",
        responses={200: MainPageSliderImageSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List MainPageSliderImages Example",
                summary="Example of listing all main page slider images",
                value=[
                    {
                        "id": 1,
                        "order": 1,
                        "link": "http://example.com",
                        "image_text": "Image 1",
                        "button_text": "Button 1",
                        "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp"
                    },
                    {
                        "id": 2,
                        "order": 2,
                        "link": "http://example.com",
                        "image_text": "Image 2",
                        "button_text": "Button 2",
                        "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp"
                    },
                    {
                        "id": 3,
                        "order": 3,
                        "link": "http://example.com",
                        "image_text": "Image 3",
                        "button_text": "Button 3",
                        "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp"
                    },
                ],
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="This endpoint retrieves a specific main page slider image by its ID.",
        responses={200: MainPageSliderImageSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve MainPageSliderImage Example",
                summary="Example of retrieving a specific main page slider image",
                value={
                    "id": 1,
                    "order": 1,
                    "link": "http://example.com",
                    "image_text": "Image 1",
                    "button_text": "Button 1",
                    "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp"
                },
                response_only=True,
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="This endpoint creates a new main page slider image.",
        request=MainPageSliderImageSerializer,
        responses={201: MainPageSliderImageSerializer()},
        examples=[
            OpenApiExample(
                name="Create MainPageSliderImage Example",
                summary="Example of creating a new main page slider image",
                value={
                    "order": 4,
                    "link": "http://example.com",
                    "image_text": "Image 4",
                    "button_text": "Button 4",
                    "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp"
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Create MainPageSliderImage Response Example",
                summary="Example of response after creating a new main page slider image",
                value={
                    "id": 4,
                    "order": 4,
                    "link": "http://example.com",
                    "image_text": "Image 4",
                    "button_text": "Button 4",
                    "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp"
                },
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="This endpoint updates a specific main page slider image by its ID.",
        request=MainPageSliderImageSerializer,
        responses={200: MainPageSliderImageSerializer()},
        examples=[
            OpenApiExample(
                name="Update MainPageSliderImage Example",
                summary="Example of updating a specific main page slider image",
                value={
                    "id": 1,
                    "order": 1,
                    "link": "http://example.com",
                    "image_text": "Updated Image 1",
                    "button_text": "Updated Button 1",
                    "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp"
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Update MainPageSliderImage Response Example",
                summary="Example of response after updating a specific main page slider image",
                value={
                    "id": 1,
                    "order": 1,
                    "link": "http://example.com",
                    "image_text": "Updated Image 1",
                    "button_text": "Updated Button 1",
                    "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp"
                },
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="This endpoint partially updates a specific main page slider image by its ID.",
        request=MainPageSliderImageSerializer,
        responses={200: MainPageSliderImageSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update MainPageSliderImage Example",
                summary="Example of partially updating a specific main page slider image",
                value={"image_text": "Updated Image 1"},
                request_only=True,
            ),
            OpenApiExample(
                name="Partial Update MainPageSliderImage Response Example",
                summary="Example of response after partially updating a specific main page slider image",
                value={
                    "id": "1",
                    "name": 1,
                    "order": 1,
                    "link": "http://example.com",
                    "image_text": "Updated Image 1",
                    "button_text": "Button 1",
                    "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp"
                },
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="This endpoint deletes a specific main page slider image by its ID.",
        responses={204: None},
        examples=[
            OpenApiExample(
                name="Delete MainPageSliderImage Example",
                summary="Example of deleting a specific main page slider image",
                value=None,
            )
        ],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
