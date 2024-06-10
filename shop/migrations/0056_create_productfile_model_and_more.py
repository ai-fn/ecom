# Generated by Django 4.2.11 on 2024-06-04 10:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0055_alter_characteristicvalue_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='characteristicvalue',
            name='slug',
            field=models.SlugField(max_length=1024, verbose_name='Слаг'),
        ),
        migrations.AlterField(
            model_name='characteristicvalue',
            name='value',
            field=models.CharField(max_length=1024, verbose_name='Значение'),
        ),
        migrations.AlterField(
            model_name='product',
            name='catalog_image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='catalog/products/images/', verbose_name='Изображение в каталоге'),
        ),
        migrations.AlterField(
            model_name='product',
            name='original_image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='catalog/products/images/', verbose_name='Исходное изображение'),
        ),
        migrations.AlterField(
            model_name='product',
            name='search_image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='catalog/products/images/', verbose_name='Изображение в поиске'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(max_length=255, upload_to='catalog/products/images/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
        migrations.CreateModel(
            name='ProductFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=512, verbose_name='Наименование')),
                ('file', models.FileField(max_length=512, upload_to='catalog/products/documents/', verbose_name='Файл')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='shop.product', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Документация',
                'verbose_name_plural': 'Документация',
            },
        ),
        migrations.AlterUniqueTogether(
            name='productfile',
            unique_together={('product', 'name')},
        ),
    ]