# Generated by Django 4.2.8 on 2024-02-05 12:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_alter_characteristic_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='characteristic',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='characteristics', to='shop.category'),
        ),
    ]
