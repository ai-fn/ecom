# Generated by Django 4.2.10 on 2024-03-04 06:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_product_similar_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='shop.brand', verbose_name='Бренд'),
        ),
        migrations.AlterField(
            model_name='product',
            name='similar_products',
            field=models.ManyToManyField(blank=True, to='shop.product', verbose_name='Похожие продукты'),
        ),
    ]
