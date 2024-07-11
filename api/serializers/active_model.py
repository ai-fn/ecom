from rest_framework import serializers


class ActiveModelSerializerMetaClass(serializers.SerializerMetaclass):

    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if hasattr(new_class, 'Meta'):
            meta = new_class.Meta
            if hasattr(meta, 'exclude'):
                pass
            elif hasattr(meta, 'fields'):
                meta.fields = list(meta.fields) + ['is_active']
            else:
                meta.fields = ['is_active']
        return new_class


class ActiveModelSerializer(serializers.ModelSerializer, metaclass=ActiveModelSerializerMetaClass):
    is_active = serializers.BooleanField(default=True)

    class Meta:
        abstract = True
