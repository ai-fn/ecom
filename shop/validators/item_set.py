from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType


def validate_object_exists(content_type: ContentType, object_id: int) -> None:
    """
    Проверяет существование объекта с указанным идентификатором в модели, заданной `content_type`.

    :param content_type: Экземпляр ContentType, указывающий на модель.
    :type content_type: ContentType
    :param object_id: Идентификатор объекта для проверки.
    :type object_id: int
    :raises ValidationError: Если объект с указанным ID не существует.
    """
    model_class = content_type.model_class()
    if not model_class.objects.filter(pk=object_id).exists():
        raise ValidationError(
            f"Object with ID {object_id} does not exist in {content_type.model}."
        )
