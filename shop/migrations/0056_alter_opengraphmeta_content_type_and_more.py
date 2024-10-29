# Generated by Django 4.2.11 on 2024-10-29 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0055_alter_opengraphmeta_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opengraphmeta',
            name='content_type',
            field=models.CharField(choices=[('PAGE', 'Страница'), ('BRAND', 'Бренд'), ('PRODUCT', 'Товар'), ('CATEGORY', 'Категория'), ('PAGE_DEFAULT', 'Страница по умолчанию'), ('BRAND_DEFAULT', 'Бренд по умолчанию'), ('PRODUCT_DEFAULT', 'Товар по умолчанию'), ('CATEGORY_DEFAULT', 'Категория по умолчанию')], max_length=128, verbose_name='Тип объекта метаданных'),
        ),
        migrations.AlterField(
            model_name='opengraphmeta',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='ID объекта'),
        ),
    ]
