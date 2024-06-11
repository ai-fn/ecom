import pymorphy2

from django.db.models.signals import (
    pre_save,
)
from django.dispatch import receiver

from .models import City

morth = pymorphy2.MorphAnalyzer()

@receiver(pre_save, sender=City)
def set_cases(sender, instance, **kwargs):
    set_case = lambda parsed_word, case: parsed_word.inflect({case}).word.title() if parsed_word.inflect({case}) is not None else parsed_word.word
    parsed_city_name = morth.parse(instance.name)[0]
    instance.nominative_case = instance.name.title()
    instance.genitive_case = set_case(parsed_city_name, "gent")
    instance.dative_case = set_case(parsed_city_name, "datv")
    instance.accusative_case = set_case(parsed_city_name, "accs")
    instance.instrumental_case = set_case(parsed_city_name, "ablt")
    instance.prepositional_case = set_case(parsed_city_name, "loct")
