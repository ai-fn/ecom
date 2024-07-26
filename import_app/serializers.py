from rest_framework import serializers

from api.serializers.active_model import ActiveModelSerializer

from import_app.models import ImportTask, ImportSetting


class ImportTaskSerializer(ActiveModelSerializer):

    class Meta:
        model = ImportTask
        exclude = ["updated_at"]

    def get_status(self, obj) -> str:
        return obj.get_status_display()

    def run_validation(self, data):
        if 'user' not in data:
            if request_user := getattr(self.context.get("request"), "user", None):
                data['user'] = request_user.pk

        return super().run_validation(data)


class ImportSettingSerializer(ActiveModelSerializer):

    items_not_in_file_action = serializers.ChoiceField(choices=ImportSetting.ITEMS_NOT_IN_FILE_ACTION_CHOICES, required=False)
    inactive_items_action = serializers.ChoiceField(choices=ImportSetting.INACTICE_ITEMS_ACTION_CHOICES, required=False)

    class Meta:
        model = ImportSetting
        exclude = ["updated_at", "name", "slug"]

    def get_inactive_items_action(self, obj) -> str:
        return obj.get_inactive_items_action_display()

    def get_items_not_in_file_action_choices(self, obj) -> str:
        return obj.get_items_not_in_file_action_choices_display()
    
    def get_file(self, obj) -> str | None:
        return obj.file.url if obj.file else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['import_task'] = ImportTaskSerializer(instance["import_task"]).data
        return data
