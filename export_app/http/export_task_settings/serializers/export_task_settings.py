from export_app.models import ExportSettings
from rest_framework.serializers import ModelSerializer, CharField, SlugField, empty


class ExportSettingsSerializer(ModelSerializer):

    class Meta:
        model = ExportSettings
        exclude = [
            "created_at",
            "updated_at",
        ]
    
    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if not self.context.get("save_settings"):
            self.fields["name"] = CharField(required=False, max_length=256)
            self.fields["slug"] = SlugField(required=False, max_length=256)


class SimplifiedSettingsSerializer(ModelSerializer):

    class Meta:
        model = ExportSettings
        fields = [
            "id",
            "name",
            "slug",
        ]
