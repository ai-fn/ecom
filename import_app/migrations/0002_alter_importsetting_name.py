# Generated by Django 4.2.11 on 2024-07-29 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('import_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importsetting',
            name='name',
            field=models.CharField(max_length=256, unique=True, verbose_name='Наименование'),
        ),
    ]
