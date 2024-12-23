from django.core.exceptions import ValidationError


IMPORT_FILE_MAX_SIZE = 5 # Mb

def size_validate(value):
    """
    Проверяет размер загружаемого файла.

    :param value: Загружаемый файл.
    :raises ValidationError: Если размер файла превышает установленный лимит.
    """

    if getattr(value, "size") > IMPORT_FILE_MAX_SIZE * 1024 * 1024:
        raise ValidationError(f"File size must not exceed {IMPORT_FILE_MAX_SIZE}Mb.")
