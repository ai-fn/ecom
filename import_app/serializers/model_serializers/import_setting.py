from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from collections import OrderedDict
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.settings import api_settings
from rest_framework.fields import SkipField, get_error_detail, set_value
from rest_framework.validators import UniqueValidator
from collections.abc import Mapping

from api.serializers.active_model import ActiveModelSerializer

from import_app.models import ImportSetting
from import_app.serializers.model_serializers import ImportTaskSerializer


class ImportSettingSerializer(ActiveModelSerializer):

    items_not_in_file_action = serializers.ChoiceField(choices=ImportSetting.ITEMS_NOT_IN_FILE_ACTION_CHOICES, required=False)
    inactive_items_action = serializers.ChoiceField(choices=ImportSetting.INACTICE_ITEMS_ACTION_CHOICES, required=False)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = ImportSetting
        exclude = ["updated_at", "created_at"]
        extra_kwargs = {"slug": {"read_only": True}}

    def get_file(self, obj) -> str | None:
        return obj.file.url if obj.file else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance, OrderedDict):
            import_task = instance.get("import_task")
        else:
            import_task = getattr(instance, "import_task", None)

        data['import_task'] = ImportTaskSerializer(import_task).data
        return data

    def to_internal_value(self, data):
        """
        Dict of native values <- Dict of primitive datatypes.
        """
        if not isinstance(data, Mapping):
            message = self.error_messages['invalid'].format(
                datatype=type(data).__name__
            )
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='invalid')

        ret = OrderedDict()
        errors = OrderedDict()
        fields = self._writable_fields

        for field in fields:
            validate_method = getattr(self, 'validate_' + field.field_name, None)
            primitive_value = field.get_value(data)
            try:
                if not self.context.get('save_settings', False):
                    original_validators = field.validators
                    field.validators = [v for v in field.validators if not isinstance(v, UniqueValidator)]

                validated_value = field.run_validation(primitive_value)

                if not self.context.get('save_settings', False):
                    field.validators = original_validators

                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except ValidationError as exc:
                errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                errors[field.field_name] = get_error_detail(exc)
            except SkipField:
                pass
            else:
                set_value(ret, field.source_attrs, validated_value)

        if errors:
            raise ValidationError(errors)

        return ret
