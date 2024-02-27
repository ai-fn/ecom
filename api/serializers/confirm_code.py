from rest_framework import serializers


class ConfirmCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4, min_length=4)
