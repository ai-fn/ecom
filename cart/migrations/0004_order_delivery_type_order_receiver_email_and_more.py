# Generated by Django 4.2.11 on 2024-11-12 08:51

from django.db import migrations, models


def set_added_fields(apps, schema_editor):
    Order = apps.get_model('cart', 'Order')
    for order in Order.objects.all():
        order.delivery_type = Order.DeliveryType.DELIVERY
        order.receiver_email = getattr(order.customer.email, "Почта не указана")
        order.receiver_first_name = getattr(order.customer.receiver_first_name, "Имя получателя не указано")
        order.receiver_last_name = getattr(order.customer.receiver_last_name, "Фамилия получателя не указана")
        order.receiver_phone = getattr(order.customer.receiver_phone, "Номер не указан")
        order.save()

    return


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_alter_order_options_alter_productsinorder_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_type',
            field=models.CharField(choices=[('delivery', 'Доставка'), ('pickup', 'Пункт выдачи')], default='delivery', max_length=30, verbose_name='Тип доставки', blank=True, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='receiver_email',
            field=models.EmailField(help_text='Адрес электронной почты получателя', max_length=254, verbose_name='Почта', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='receiver_first_name',
            field=models.CharField(default='123', max_length=100, verbose_name='Имя получателя', blank=True, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='receiver_last_name',
            field=models.CharField(default='sdafa', max_length=100, verbose_name='Фамилия получателя', blank=True, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='receiver_phone',
            field=models.CharField(help_text='В формате +7xxxxxxxxxx', max_length=16, verbose_name='Номер телефона получателя', blank=True, null=True),
        ),

        migrations.RunPython(set_added_fields, migrations.RunPython.noop),

        migrations.AlterField(
            model_name='order',
            name='delivery_type',
            field=models.CharField(choices=[('delivery', 'Доставка'), ('pickup', 'Пункт выдачи')], default='delivery', max_length=30, verbose_name='Тип доставки'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='receiver_email',
            field=models.EmailField(blank=True, help_text='Адрес электронной почты получателя', max_length=254, null=True, verbose_name='Почта'),
        ),
        migrations.AlterField(
            model_name='order',
            name='receiver_first_name',
            field=models.CharField(default='123', max_length=100, verbose_name='Имя получателя'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='receiver_last_name',
            field=models.CharField(default='sdafa', max_length=100, verbose_name='Фамилия получателя'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='receiver_phone',
            field=models.CharField(blank=True, help_text='В формате +7xxxxxxxxxx', max_length=16, null=True, verbose_name='Номер телефона получателя'),
        ),
    ]