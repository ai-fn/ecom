# Generated by Django 4.2.11 on 2024-03-27 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_alter_customuser_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='address',
            new_name='region',
        ),
        migrations.AddField(
            model_name='customuser',
            name='city_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Город'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='district',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Район'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='house',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Номер дома'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='street',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Улица'),
        ),
    ]
