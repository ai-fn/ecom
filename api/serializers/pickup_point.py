from rest_framework.serializers import ModelSerializer, SerializerMethodField, DecimalField
from api.mixins import ValidatePhoneNumberMixin
from cart.models import PickupPoint, PickupPointSchedule
from api.serializers import ActiveModelSerializer


class PickupPointDetailSerializer(ModelSerializer):
    coord_x = DecimalField(max_digits=9, decimal_places=6, coerce_to_string=False)
    coord_y = DecimalField(max_digits=9, decimal_places=6, coerce_to_string=False)

    class Meta:
        model = PickupPoint
        fields = "__all__"


class PickupPointSerializer(ModelSerializer, ValidatePhoneNumberMixin):
    coordinate = SerializerMethodField()
    worktime = SerializerMethodField()

    class Meta:
        model = PickupPoint
        fields = [
            "id",
            "address",
            "coordinate",
            "worktime",
            "phone",
        ]

    def validate_phone(self, value):
        self.phone_is_valid(value)
        return value

    def get_coordinate(self, obj) -> list:
        return [float(obj.coord_x), float(obj.coord_y)]

    def get_worktime(self, obj) -> list:
        return [item.schedule for item in obj.schedules.filter(is_active=True)]


class PickupPointScheduleSerializer(ActiveModelSerializer):
    class Meta:
        model =  PickupPointSchedule
        fields = [
            "id",
            "title",
            "order",
            "pickup_point",
            "schedule",
        ]
