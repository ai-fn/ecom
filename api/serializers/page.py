import pymorphy2

from shop.models import Page
from api.serializers import ActiveModelSerializer


morph = pymorphy2.MorphAnalyzer()


class PageSerializer(ActiveModelSerializer):

    class Meta:
        model = Page
        fields = [
            "id",
            "slug",
            "image",
            "title",
            "h1_tag",
            "content",
            "description",
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

        return data
