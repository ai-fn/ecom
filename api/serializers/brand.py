from rest_framework import serializers

from shop.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "icon",
            "order",
            "slug",
        ]
    
    def get_icon(self, obj) -> str | None:
        return obj.icon.url if obj.icon else None
