from rest_framework.serializers import Serializer, CharField


class InfoResponseSerializer(Serializer):
    detail = CharField()
