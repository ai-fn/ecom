# Generated by Django 4.2.11 on 2024-07-11 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активность'),
        ),
    ]