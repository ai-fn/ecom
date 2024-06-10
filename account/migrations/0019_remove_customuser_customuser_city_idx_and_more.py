# Generated by Django 4.2.11 on 2024-06-05 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_alter_customuser_first_name_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='customuser',
            name='customuser_city_idx',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='city',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='city_name',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='district',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='house',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='region',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='street',
        ),
        migrations.AddField(
            model_name='customuser',
            name='address',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='Адрес'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, help_text='Адрес электронной почты', max_length=254, null=True, verbose_name='Почта'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=35, null=True, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=35, null=True, verbose_name='Фамилия '),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['address'], name='customuser_address_idx'),
        ),
    ]