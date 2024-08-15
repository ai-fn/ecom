# Generated by Django 4.2.11 on 2024-08-15 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('P', 'Создан'), ('PR', 'В обработке'), ('S', 'Отправлен'), ('D', 'Доставлен')], default='P', max_length=20, verbose_name='Статус заказа'),
        ),
        migrations.DeleteModel(
            name='OrderStatus',
        ),
    ]
