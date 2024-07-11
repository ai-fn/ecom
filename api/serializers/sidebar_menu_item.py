from api.serializers import ActiveModelSerializer

from shop.models import SideBarMenuItem


class SideBarMenuItemSerializer(ActiveModelSerializer):
    
    class Meta:
        model = SideBarMenuItem
        exclude = ["created_at", "updated_at"]
