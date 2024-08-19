from rest_framework import serializers
from rest_framework.fields import empty

from api.serializers.active_model import ActiveModelSerializer

from import_app.models import ImportSetting


class ImportSettingSerializer(ActiveModelSerializer):

    items_not_in_file_action = serializers.ChoiceField(choices=ImportSetting.ITEMS_NOT_IN_FILE_ACTION_CHOICES, required=False)
    inactive_items_action = serializers.ChoiceField(choices=ImportSetting.INACTICE_ITEMS_ACTION_CHOICES, required=False)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = ImportSetting
        exclude = [
            "updated_at",
            "created_at",
        ]


    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if not self.context.get("save_settings", False):
            self.fields["name"] = serializers.CharField(max_length=256, required=False)
            self.fields["slug"] = serializers.SlugField(max_length=512, required=False)
