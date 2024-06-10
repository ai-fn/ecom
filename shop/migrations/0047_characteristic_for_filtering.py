# Generated by Django 4.2.11 on 2024-05-23 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0046_characteristic_slug_alter_characteristic_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='characteristic',
            name='for_filtering',
            field=models.BooleanField(blank=True, default=False, help_text='Будет ли эта характеристика отображаться в фильтрах товаров', verbose_name='Для фильтрации'),
        ),
    ]