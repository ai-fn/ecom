# Generated by Django 4.2.11 on 2024-08-26 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0040_alter_brand_options_alter_category_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promo',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активность'),
        ),
    ]