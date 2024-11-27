# Generated by Django 4.2.11 on 2024-11-26 11:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0006_pickuppoint_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickuppoint',
            name='phone',
            field=models.CharField(blank=True, help_text='В формате +7xxxxxxxxxx', max_length=16, null=True, verbose_name='Номер телефона'),
        ),
        migrations.CreateModel(
            name='PickupPointSchedule',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Активность')),
                ('schedule', models.CharField(max_length=256, verbose_name='График работы')),
                ('title', models.CharField(blank=True, max_length=128, null=True, verbose_name='Заголовок')),
                ('order', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Порядковый номер')),
                ('pickup_point', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='cart.pickuppoint', verbose_name='Пункт выдачи')),
            ],
            options={
                'verbose_name': 'График работы пункта выдачи',
                'verbose_name_plural': 'Графики работы пунктов выдачи',
                'ordering': ('pickup_point', 'order', '-created_at'),
                'indexes': [models.Index(fields=['title'], name='schedule_title_idx'), models.Index(fields=['schedule'], name='schedule_schedule_idx')],
            },
        ),
    ]