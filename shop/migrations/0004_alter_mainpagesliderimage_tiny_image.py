# Generated by Django 4.2.11 on 2024-07-02 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_mainpagesliderimage_tiny_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainpagesliderimage',
            name='tiny_image',
            field=models.ImageField(null=True, upload_to='main/sliders/tiny', verbose_name='Маленькое изображение'),
        ),
    ]
