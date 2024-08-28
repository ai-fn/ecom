from api.serializers import ActiveModelSerializer
from shop.models import Characteristic
from rest_framework.serializers import SerializerMethodField


class CharacteristicFilterSerializer(ActiveModelSerializer):

    values = SerializerMethodField()

    class Meta:
        model = Characteristic
        fields = ["name", "slug", "values"]

    def get_values(self, obj):
        queryset = self.context.get("queryset", tuple())
        return (
            obj.characteristicvalue_set.filter(product__in=queryset)
            .values("value", "slug")
            .order_by("slug")
            .distinct("slug")
        )
