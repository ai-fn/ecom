from rest_framework.serializers import ModelSerializer, SerializerMethodField

from shop.models import SideBarMenuItem


class SideBarMenuItemSerializer(ModelSerializer):
    
    class Meta:
        model = SideBarMenuItem
        exclude = ["created_at", "updated_at"]
