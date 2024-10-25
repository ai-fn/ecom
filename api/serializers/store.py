from api.serializers import ActiveModelSerializer
from api.serializers.phone import PhoneSerializer
from account.models import Store
from rest_framework.serializers import SerializerMethodField



class StoreSerializer(ActiveModelSerializer, PhoneSerializer):
    schedules = SerializerMethodField()

    class Meta:
        model =  Store
        fields = [
            "id",
            "name",
            "phone",
            "address",
            "schedules"
        ]
    
    def get_schedules(self, obj: Store) -> list[str | None]:
        schedules = obj.schedules.filter(is_active=True)
        return [x.schedule for x in schedules]
