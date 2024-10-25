import phonenumbers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ValidatePhoneNumberMixin:

    def validate_phone(self, value):
        phone = value
        try:
            parsed_number = phonenumbers.parse(phone, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError(_("Неверный номер телефона."))
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValidationError(_("Неверный номер телефона."))

        return value
