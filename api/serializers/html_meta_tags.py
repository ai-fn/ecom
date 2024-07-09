from rest_framework import serializers
from shop.models import HTMLMetaTags
from django.contrib.contenttypes.models import ContentType


class HTMLMetaTagSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field='model'
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        query_params = getattr(self.context.get("request"), "query_params", {})

        city_domain = query_params.get("city_domain")
        for attr in ("title", "keywords", "description"):
            data[attr] = instance.get_formatted_meta_tag(attr, city_domain)

        return data 
