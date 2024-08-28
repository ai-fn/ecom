from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


@deconstructible
class FileSizeValidator:
    message = _(
        "Размер файла “%(file_size)s”Mb не допустим. "
        "Максимально допустимый размер: %(max_size)sMb. "
    )
    code = "invalid_size"

    def __init__(self, size: int | float) -> None:
        self.size = size
    
    def __call__(self, value):
        max_size = self.size * 1024 * 1024

        if value.size > max_size:
            raise ValidationError(
                message=self.message,
                code=self.code,
                params={
                    "file_size": value.size,
                    "max_size": self.size,
                    "value": value
                }
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.size == other.size
            and self.message == other.message
            and self.code == other.code
        )
