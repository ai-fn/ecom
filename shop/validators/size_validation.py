from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


@deconstructible
class FileSizeValidator:
    """
    Валидатор для проверки размера файла.

    :param size: Максимально допустимый размер файла в мегабайтах.
    :type size: int | float
    """
    message = _(
        "Размер файла “%(file_size)s”Mb не допустим. "
        "Максимально допустимый размер: %(max_size)sMb. "
    )
    code = "invalid_size"

    def __init__(self, size: int | float) -> None:
        """
        Инициализация валидатора.

        :param size: Максимально допустимый размер файла в мегабайтах.
        """
        self.size = size

    def __call__(self, value):
        """
        Выполняет валидацию файла.

        :param value: Файл для проверки.
        :raises ValidationError: Если размер файла превышает допустимый.
        """
        max_size = self.size * 1024 * 1024

        if value.size > max_size:
            raise ValidationError(
                message=self.message,
                code=self.code,
                params={
                    "file_size": round(value.size / (1024 * 1024), 2),  # Конвертация в MB
                    "max_size": self.size,
                    "value": value,
                },
            )

    def __eq__(self, other) -> bool:
        """
        Проверяет эквивалентность двух валидаторов.

        :param other: Другой валидатор.
        :return: True, если валидаторы эквивалентны, иначе False.
        """
        return (
            isinstance(other, self.__class__)
            and self.size == other.size
            and self.message == other.message
            and self.code == other.code
        )
