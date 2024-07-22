# Generated by Django 4.2.11 on 2024-07-19 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bitrix_app', '0002_lead_dynamical_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='bitrix_id',
            field=models.IntegerField(blank=True, null=True, unique=True, verbose_name='Идентификатор Bitrix24'),
        ),
    ]