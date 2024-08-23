from django.core.exceptions import ValidationError


def validate_object_exists(content_type, object_id):
    model_class = content_type.model_class()
    if not model_class.objects.filter(pk=object_id).exists():
        raise ValidationError(f"Object with ID {object_id} does not exist in {content_type.model}.")
