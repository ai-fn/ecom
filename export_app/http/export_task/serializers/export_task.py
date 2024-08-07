from copy import deepcopy
from collections import OrderedDict
from rest_framework.serializers import ModelSerializer

from export_app.models import ExportTask
from export_app.http.export_task_settings.serializers import ExportSettingsSerializer


class ExportTaskSerializer(ModelSerializer):

    settings = ExportSettingsSerializer()

    class Meta:
        model = ExportTask
        exclude = [
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if isinstance(instance, OrderedDict):
            data["result_file"] = instance["result_file"].url if instance["result_file"] else None
            
            settings_data = self.initial_data.get("settings")
            if settings_data:
                stngs_serializer = ExportSettingsSerializer(data=settings_data)
                if stngs_serializer.is_valid():
                    data["settings"] = stngs_serializer.data
                else:
                    data["settings"] = None
            else:
                data["settings"] = None

        else:
            data["result_file"] = instance.result_file.url if instance.result_file else None
            data["settings"] = ExportSettingsSerializer(instance=instance.settings).data if instance.settings else None

        return data

    def run_validation(self, data):
        mutable_data = deepcopy(data)
        if "user" not in mutable_data:
            if request_user := getattr(self.context.get("request"), "user", None):
                mutable_data["user"] = request_user.pk

        return super().run_validation(mutable_data)

    def save(self, **kwargs):
        if not self.context.get("save_settings"):
            self.validated_data.pop("settings")

        return super().save(**kwargs)
