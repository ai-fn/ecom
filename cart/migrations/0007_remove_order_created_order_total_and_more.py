# Generated by Django 4.2.11 on 2024-03-28 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0006_merge_20240328_1133'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='created',
        ),
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Сумма заказа'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productsinorder',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Цена товара на момент заказа'),
            preserve_default=False,
        ),
    ]