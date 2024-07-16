# Generated by Django 4.2.11 on 2024-07-10 12:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='citygroup',
            name='cities',
        ),
        migrations.AddField(
            model_name='city',
            name='city_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="cities", to='account.citygroup', verbose_name='Группа городов'),
        ),
        migrations.AlterField(
            model_name='citygroup',
            name='main_city',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='main_in_group', to='account.city', verbose_name='Главный город'),
        ),
        migrations.AlterField(
            model_name='city',
            name='address',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Адрес'),
        ),
        migrations.AlterField(
            model_name='city',
            name='how_to_get_office',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Как добраться до офиса'),
        ),
        migrations.AlterField(
            model_name='city',
            name='domain',
            field=models.CharField(max_length=255, null=True, unique=True, verbose_name='Домен'),
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(max_length=255, null=True, unique=True, verbose_name='Город'),
        ),
    ]