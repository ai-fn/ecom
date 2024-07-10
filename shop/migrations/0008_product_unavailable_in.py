# Generated by Django 4.2.11 on 2024-07-09 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
        ('shop', '0007_alter_htmlmetatags_keywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='unavailable_in',
            field=models.ManyToManyField(related_query_name='product', to='account.city', verbose_name='Недоступен в городах', blank=True),
        ),
    ]
