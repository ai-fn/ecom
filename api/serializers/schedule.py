from api.serializers import ActiveModelSerializer
from account.models import Schedule


class ScheduleSerializer(ActiveModelSerializer):
    class Meta:
        model =  Schedule
        fields = [
            "id",
            "title",
            "order",
            "store",
            "schedule",
        ]
