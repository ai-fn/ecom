# Generated by Django 4.2.11 on 2024-11-14 08:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def set_cities(apps, schema_editor):
    City = apps.get_model("account", "City")
    PickupPoint = apps.get_model("cart", "PickupPoint")
    default_city = City.objects.get(name=settings.DEFAULT_CITY_NAME)

    for pp in PickupPoint.objects.all():
        pp.city = default_city
        pp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_alter_citygroup_options'),
        ('cart', '0005_pickuppoint'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickuppoint',
            name='city',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, to='account.city', verbose_name='Город', null=True),
            preserve_default=False,
        ),
        migrations.RunPython(set_cities, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='pickuppoint',
            name='city',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, to='account.city', verbose_name='Город'),
            preserve_default=False,
        ),
    ]
