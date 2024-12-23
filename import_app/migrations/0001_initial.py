# Generated by Django 4.2.11 on 2024-07-26 08:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import import_app.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportTask',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Активность')),
                ('file', models.FileField(upload_to=import_app.models.get_default_file_upload_path, verbose_name='Файл импорта')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], default='PENDING', max_length=20, verbose_name='Статус')),
                ('end_at', models.DateTimeField(blank=True, null=True, verbose_name='Окончен')),
                ('comment', models.TextField(blank=True, max_length=1024, null=True, verbose_name='Комментарий')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Импорт',
                'verbose_name_plural': 'Импорты',
            },
        ),
        migrations.CreateModel(
            name='ImportSetting',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Активность')),
                ('name', models.CharField(max_length=256, verbose_name='Наименование')),
                ('slug', models.SlugField(max_length=512, unique=True, verbose_name='Слаг')),
                ('fields', models.JSONField(unique=True, verbose_name='Соотношение полей')),
                ('path_to_images', models.CharField(blank=True, default=import_app.models.get_default_images_upload_path, max_length=255, null=True)),
                ('items_not_in_file_action', models.CharField(choices=[('DEACTIVATE', 'деактивировать'), ('DELETE', 'удалить'), ('SET_NOT_IN_STOCK', 'установить статус "нет в наличии"'), ('IGNORE', 'не трогать')], default='IGNORE', max_length=50)),
                ('inactive_items_action', models.CharField(choices=[('LEAVE', 'оставить как есть'), ('ACTIVATE', 'активировать')], default='LEAVE', max_length=50)),
                ('remove_existing_price_if_empty', models.BooleanField(default=False)),
                ('import_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='import_app.importtask', verbose_name='Импорт')),
            ],
            options={
                'verbose_name': 'Шаблон импорта',
                'verbose_name_plural': 'Шаблоны импорта',
            },
        ),
    ]
