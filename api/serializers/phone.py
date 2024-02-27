import phonenumbers

from rest_framework import serializers

class PhoneSerializer(serializers.Serializer):
    
    phone_number = serializers.CharField(max_length=16)

    def validate_phone_number(self, value):
        phone_number = value
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError("Invalid phone number.")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise serializers.ValidationError("Invalid phone number.")

        return value
