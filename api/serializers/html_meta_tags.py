from api.serializers import ActiveModelSerializer
from shop.models import HTMLMetaTags
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers


class HTMLMetaTagSerializer(ActiveModelSerializer):
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(), slug_field="model"
    )

    class Meta:
        model = HTMLMetaTags
        fields = [
            "id",
            "title",
            "description",
            "keywords",
            "object_id",
            "content_type",
        ]

    def to_representation(self, instance: HTMLMetaTags):
        data = super().to_representation(instance)
        query_params = getattr(self.context.get("request"), "query_params", {})

        city_domain = query_params.get("city_domain")
        kwargs = {"city_domain": city_domain}
        if (inst := self.context.get("instance")):
            kwargs['instance'] = inst
            data['content_type'] = inst._meta.model_name
            data['object_id'] = inst.id
            get_meta_tag = instance.get_formatted_meta_tag_by_instance
        else:
            get_meta_tag = instance.get_formatted_meta_tag

        for attr in ("title", "keywords", "description"):
            kwargs['field'] = attr
            data[attr] = get_meta_tag(**kwargs)

        return data
