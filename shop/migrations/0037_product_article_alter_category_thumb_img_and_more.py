# Generated by Django 4.2.11 on 2024-04-22 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0036_category_thumb_img_mainpagesliderimage_thumb_img_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='article',
            field=models.CharField(max_length=128, unique=True, verbose_name='Артикул'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='category',
            name='thumb_img',
            field=models.TextField(blank=True, max_length=512, null=True, verbose_name='Миниатюра'),
        ),
        migrations.AlterField(
            model_name='mainpagesliderimage',
            name='thumb_img',
            field=models.TextField(blank=True, max_length=512, null=True, verbose_name='Миниатюра'),
        ),
        migrations.AlterField(
            model_name='product',
            name='catalog_image',
            field=models.ImageField(blank=True, null=True, upload_to='catalog/products/', verbose_name='Изображение в каталоге'),
        ),
        migrations.AlterField(
            model_name='product',
            name='search_image',
            field=models.ImageField(blank=True, null=True, upload_to='catalog/products/', verbose_name='Изображение в поиске'),
        ),
        migrations.AlterField(
            model_name='product',
            name='thumb_img',
            field=models.TextField(blank=True, max_length=512, null=True, verbose_name='Миниатюра'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='thumb_img',
            field=models.TextField(blank=True, max_length=512, null=True, verbose_name='Миниатюра'),
        ),
        migrations.AlterField(
            model_name='promo',
            name='thumb_img',
            field=models.TextField(blank=True, max_length=512, null=True, verbose_name='Миниатюра'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['article'], name='shop_produc_article_6c9444_idx'),
        ),
    ]
