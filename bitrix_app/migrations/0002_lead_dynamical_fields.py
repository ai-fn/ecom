# Generated by Django 4.2.11 on 2024-07-19 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bitrix_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='dynamical_fields',
            field=models.JSONField(default=dict, verbose_name='Дополнительная информация'),
        ),
    ]
