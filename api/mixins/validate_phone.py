import phonenumbers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from account.models import CustomUser


class ValidatePhoneNumberMixin:

    def validate_phone(self, value):
        if instance := getattr(self, "instance", None):
            if getattr(instance, "phone", None) == value:
                raise ValidationError(_("Phone already confirmed"))

        phone = value
        try:
            parsed_number = phonenumbers.parse(phone, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError(_("Invalid phone number."))
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValidationError(_("Invalid phone number."))

        return value
