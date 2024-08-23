import pymorphy2

from typing import OrderedDict
from rest_framework.serializers import SerializerMethodField
from account.models import City
from api.serializers import ActiveModelSerializer, OpenGraphMetaSerializer

from shop.models import Page


morph = pymorphy2.MorphAnalyzer()


class PageSerializer(ActiveModelSerializer):
    opengraph_metadata = SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            "id",
            "title",
            "h1_tag",
            "content",
            "description",
            "slug",
            "image",
            "opengraph_metadata",
        ]
        read_only_fields = ["slug", "id"]

    def inflect_phrase(self, phrase, case):
        words = phrase.split()
        inflected_words = []

        for idx, word in enumerate(words):

            parsed = morph.parse(word)[0]
            inflected_word = parsed.inflect({case})
            
            word = inflected_word.word if inflected_word else word
            if idx == 0:
                word = word.title()
            
            inflected_words.append(word)
        
        return ' '.join(inflected_words)

    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        if instance.image:
            data["image"] = instance.image.url 

        if instance.opengraph_metadata.exists():
            data["opengraph_metadata"] = OpenGraphMetaSerializer(instance.opengraph_metadata.first()).data

        if instance.description:
            domain = self.context.get("city_domain")
            city = City.objects.filter(domain=domain).first()
            city_group = getattr(city, "city_group", None)
            city_name = getattr(city, "name", "")
            city_group_name = getattr(city_group, "name", "")

            formatters = {}
            cases = ("nomn", "gent", "datv", "accs", "ablt", "loct")
            if city is not None:
                for case in cases:
                    formatters[f"c_{case}"] = self.inflect_phrase(city_name, case)
                    formatters[f"cg_{case}"] = self.inflect_phrase(city_group_name, case)

            if formatters:
                data["description"] = instance.description.format(**formatters)

        return data

    def get_opengraph_metadata(self, obj) -> OrderedDict | None:
        if obj.opengraph_metadata.exists():
            return OpenGraphMetaSerializer(obj.opengraph_metadata.first()).data
        return None
