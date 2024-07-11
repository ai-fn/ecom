from api.serializers import ActiveModelSerializer

from shop.models import Category


class CategoryDetailSerializer(ActiveModelSerializer):

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "parent",
            "is_popular",
            "is_visible",
            "icon",
            "image",
            "order",
            "thumb_img",
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['icon'] = instance.icon.url if instance.icon else None
        data['image'] = instance.image.url if instance.image else None
        return data
