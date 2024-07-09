from rest_framework import serializers

from shop.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "icon",
            "order",
            "slug",
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['icon'] = instance.icon.url if instance.icon else None
