from copy import deepcopy
from collections import OrderedDict
from rest_framework.serializers import ModelSerializer, empty
from rest_framework.exceptions import ValidationError

from django.db import transaction

from export_app.models import ExportTask
from export_app.http.export_task_settings.serializers import ExportSettingsSerializer


class ExportTaskSerializer(ModelSerializer):

    class Meta:
        model = ExportTask
        exclude = [
            "created_at",
            "updated_at",
        ]
    
    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.fields["settings"] = ExportSettingsSerializer(context=self.context)

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

    def create(self, validated_data: dict):
        with transaction.atomic():
            if self.context.get("save_settings"):
                settings_data: dict = validated_data.pop("settings")
                serializer = ExportSettingsSerializer(data=settings_data, context=self.context)
                if not serializer.is_valid():
                    raise ValidationError(serializer.errors)

                instance = serializer.save()
                validated_data["settings"] = instance

            return super().create(validated_data)
