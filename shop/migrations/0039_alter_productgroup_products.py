# Generated by Django 4.2.11 on 2024-08-26 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0038_alter_itemset_title_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productgroup',
            name='products',
            field=models.ManyToManyField(blank=True, related_name='groups', to='shop.product', verbose_name='Продукты'),
        ),
    ]
