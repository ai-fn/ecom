from api.serializers.active_model import ActiveModelSerializer

from import_app.models import ImportTask

from copy import deepcopy


class ImportTaskSerializer(ActiveModelSerializer):

    class Meta:
        model = ImportTask
        exclude = ["updated_at"]
    
    def to_representation(self, instance):
        data =  super().to_representation(instance)
        data['file'] = instance.file.url if instance.file else None
        return data

    def run_validation(self, data):
        mutable_data = deepcopy(data)
        if 'user' not in mutable_data:
            if request_user := getattr(self.context.get("request"), "user", None):
                mutable_data['user'] = request_user.pk

        return super().run_validation(mutable_data)
