# Generated by Django 4.2.11 on 2024-06-24 13:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0010_remove_order_city_name_remove_order_district_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderstatus',
            options={'verbose_name': 'Статус заказа', 'verbose_name_plural': 'Статусы заказа'},
        ),
    ]
