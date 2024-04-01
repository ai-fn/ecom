# Generated by Django 4.2.11 on 2024-04-01 10:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0026_alter_product_in_stock_alter_product_is_popular'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='priority',
            field=models.IntegerField(default=500, validators=[django.core.validators.MaxValueValidator(1000000), django.core.validators.MinValueValidator(1)], verbose_name='Приоритет показа'),
        ),
    ]
