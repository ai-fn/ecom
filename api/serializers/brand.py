from rest_framework import serializers

from shop.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    icon = serializers.ImageField(write_only=True)
    icon_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "icon",
            "icon_url",
            "order",
            "slug",
        ]
    
    def get_icon_url(self, obj) -> str | None:
        return obj.icon.url if obj.icon else None
