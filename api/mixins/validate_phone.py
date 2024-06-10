import phonenumbers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ValidatePhoneNumberMixin:

    def validate_phone_number(self, value):
        phone_number = value
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError(_("Invalid phone number."))
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValidationError(_("Invalid phone number."))

        return value
