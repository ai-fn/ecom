from rest_framework.serializers import ModelSerializer, BooleanField
from rest_framework.fields import empty


class ActiveModelSerializer(ModelSerializer):

    class Meta:
        abstract = True

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.fields["is_active"] = BooleanField(default=True)
