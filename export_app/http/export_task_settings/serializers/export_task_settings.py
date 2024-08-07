from export_app.models import ExportSettings
from rest_framework.serializers import ModelSerializer


class ExportSettingsSerializer(ModelSerializer):
    class Meta:
        model = ExportSettings
        exclude = [
            "created_at",
            "updated_at",
        ]

    def __init__(self, instance=None, data=..., **kwargs):
        context = kwargs.get("context", {})

        super().__init__(instance, data, **kwargs)

        if not context.get("save_settings"):
            self.fields["name"].required = False
            self.fields["fields"].unique = False
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data