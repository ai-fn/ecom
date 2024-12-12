# Generated by Django 4.2.11 on 2024-10-25 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_alter_citygroup_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shedule',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Активность')),
                ('schedule', models.CharField(max_length=256, verbose_name='График работы')),
                ('title', models.CharField(blank=True, max_length=128, null=True, verbose_name='Заголовок')),
                ('order', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Порядковый номер')),
            ],
            options={
                'verbose_name': 'График работы',
                'verbose_name_plural': 'Графики работы',
                'ordering': ('store', '-created_at'),
            },
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Активность')),
                ('name', models.CharField(verbose_name='Название')),
                ('address', models.CharField(blank=True, max_length=256, null=True, verbose_name='Адрес')),
                ('phone', models.CharField(blank=True, help_text='В формате +7xxxxxxxxxx', max_length=16, null=True, unique=True, verbose_name='Номер телефона')),
            ],
            options={
                'verbose_name': 'Магазин',
                'verbose_name_plural': 'Магазины',
                'ordering': ('city', '-created_at'),
            },
        ),
        migrations.RemoveIndex(
            model_name='city',
            name='city_address_idx',
        ),
        migrations.RemoveField(
            model_name='city',
            name='address',
        ),
        migrations.RemoveField(
            model_name='city',
            name='how_to_get_office',
        ),
        migrations.RemoveField(
            model_name='city',
            name='number',
        ),
        migrations.RemoveField(
            model_name='city',
            name='schedule',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(blank=True, help_text='В формате +7xxxxxxxxxx', max_length=16, null=True, unique=True, verbose_name='Номер телефона'),
        ),
        migrations.AddField(
            model_name='store',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stores', to='account.city', verbose_name='Город'),
        ),
        migrations.AddField(
            model_name='shedule',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shedules', to='account.store', verbose_name='График работы'),
        ),
        migrations.AddIndex(
            model_name='store',
            index=models.Index(fields=['address'], name='store_address_idx'),
        ),
        migrations.AddIndex(
            model_name='store',
            index=models.Index(fields=['name'], name='store_name_idx'),
        ),
        migrations.AddIndex(
            model_name='shedule',
            index=models.Index(fields=['title'], name='str_schedule_title_idx'),
        ),
        migrations.AddIndex(
            model_name='shedule',
            index=models.Index(fields=['schedule'], name='str_schedule_schedule_idx'),
        ),
    ]