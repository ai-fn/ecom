from api.serializers.active_model import ActiveModelSerializer

from import_app.models import ImportTask


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
