from typing import OrderedDict
from rest_framework.fields import empty
from rest_framework.serializers import FileField
from api.serializers.active_model import ActiveModelSerializer

from copy import deepcopy

from import_app.models import ImportTask
from import_app.serializers.model_serializers import ImportSettingSerializer


class ImportTaskSerializer(ActiveModelSerializer):

    class Meta:
        model = ImportTask
        exclude = [
            "updated_at",
        ]


    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.fields["import_setting"] = ImportSettingSerializer(context=self.context)
        if instance:
            self.fields["file"] = FileField(required=False)


    def to_representation(self, instance):
        data =  super().to_representation(instance)
        if isinstance(instance, OrderedDict):
            import_setting_serializer = ImportSettingSerializer(data=data["import_setting"])
            import_setting_serializer.is_valid(raise_exception=True)

            data["import_setting"] = import_setting_serializer.data
        else:
            data["import_setting"] = ImportSettingSerializer(instance.import_setting).data

        data['file'] = instance.file.url if instance.file else None
        return data


    def run_validation(self, data):
        mutable_data = deepcopy(data)
        if 'user' not in mutable_data:
            if request_user := getattr(self.context.get("request"), "user", None):
                mutable_data['user'] = request_user.pk

        return super().run_validation(mutable_data)
