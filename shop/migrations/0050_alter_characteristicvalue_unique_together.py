# Generated by Django 4.2.11 on 2024-05-29 06:47

from django.db import migrations, transaction
from django.db.models import Count


def remove_duplicates(app, schema_editor):
    CharacteristicValue = app.get_model("shop", "CharacteristicValue")
    duplicates = CharacteristicValue.objects.values("characteristic", "value").annotate(count=Count("characteristic")).filter(count__gt=1)
    with transaction.atomic():
        for el in duplicates:
            duplicates_enties = CharacteristicValue.objects.filter(characteristic=el["characteristic"], value=el["value"])
            if first_el := duplicates_enties.first():
                CharacteristicValue.objects.exclude(pk=first_el.pk).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0049_characteristicvalue_slug'),
    ]

    operations = [
        migrations.RunPython(remove_duplicates, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='characteristicvalue',
            unique_together={('characteristic', 'slug')},
        ),
    ]
