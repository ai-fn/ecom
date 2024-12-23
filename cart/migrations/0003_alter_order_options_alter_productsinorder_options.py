# Generated by Django 4.2.11 on 2024-08-26 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_alter_order_status_delete_orderstatus'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('customer', '-created_at'), 'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AlterModelOptions(
            name='productsinorder',
            options={'ordering': ('order', '-created_at'), 'verbose_name': 'Товар в заказе', 'verbose_name_plural': 'Товары в заказе'},
        ),
    ]
