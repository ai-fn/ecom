# Generated by Django 4.2.11 on 2024-08-20 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0021_remove_characteristic_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.CharField(blank=True, max_length=4096, null=True, verbose_name='Описание'),
        ),
    ]
