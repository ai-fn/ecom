from account.models import Store
from api.serializers import ActiveModelSerializer
from api.serializers.phone import PhoneSerializer
from rest_framework.serializers import SerializerMethodField, DecimalField


class StoreSerializer(ActiveModelSerializer, PhoneSerializer):
    schedules = SerializerMethodField()
    coordinates = SerializerMethodField()


    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "phone",
            "address",
            "schedules",
            "coordinates",
        ]

    def get_coordinates(self, obj: Store) -> list[float, float]:
        return [float(obj.latitude), float(obj.longitude)]

    def get_schedules(self, obj: Store) -> list[str | None]:
        schedules = obj.schedules.filter(is_active=True)
        return [x.schedule for x in schedules]
