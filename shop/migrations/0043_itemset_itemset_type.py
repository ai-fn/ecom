# Generated by Django 4.2.11 on 2024-08-28 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0042_alter_price_old_price_alter_price_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemset',
            name='itemset_type',
            field=models.CharField(choices=[('product', 'Товар'), ('banner', 'Баннер')], default='product', max_length=64, verbose_name='Тип объектов набора'),
        ),
    ]
