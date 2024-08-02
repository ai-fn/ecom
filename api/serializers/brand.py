from api.serializers import ActiveModelSerializer

from shop.models import Brand
from api.serializers import ActiveModelSerializer


class BrandSerializer(ActiveModelSerializer):
    
    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "icon",
            "order",
            "h1_tag",
            "slug",
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['icon'] = instance.icon.url if instance.icon else None
        return data
