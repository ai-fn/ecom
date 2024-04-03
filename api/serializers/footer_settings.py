from rest_framework import serializers
from shop.models import FooterItem


class FooterItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FooterItem
        fields = [
            "id",
            "column",
            "order",
            "title",
            "link",
        ]
