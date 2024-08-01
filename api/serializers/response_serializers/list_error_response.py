from rest_framework.serializers import Serializer, DictField, CharField


class ListErrorResponseSerializer(Serializer):
    error = DictField(child=CharField())
