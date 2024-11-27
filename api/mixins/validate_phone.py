import phonenumbers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ValidatePhoneNumberMixin:
    """
    Mixin для валидации телефонных номеров с использованием библиотеки `phonenumbers`.
    """

    def phone_is_valid(self, value: str) -> str:
        """
        Проверяет, является ли переданный номер телефона валидным.

        :param value: Номер телефона для проверки.
        :type value: str
        :return: Входное значение, если номер телефона валиден.
        :rtype: str
        :raises ValidationError: Если номер телефона невалиден.
        """
        try:
            parsed_number = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError(_("Неверный номер телефона."))
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValidationError(_("Неверный номер телефона."))

        return value
