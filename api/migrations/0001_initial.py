# Generated by Django 4.2.11 on 2024-11-19 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApiKey',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Активность')),
                ('key', models.CharField(max_length=512, unique=True, verbose_name='API ключ')),
                ('client_id', models.PositiveBigIntegerField(unique=True, verbose_name='ID клиента')),
            ],
            options={
                'verbose_name': 'API Ключ',
                'verbose_name_plural': 'API Ключи',
                'ordering': ('-created_at',),
            },
        ),
    ]
