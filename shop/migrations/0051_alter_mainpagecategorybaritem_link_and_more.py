# Generated by Django 4.2.11 on 2024-05-29 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0050_alter_characteristicvalue_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainpagecategorybaritem',
            name='link',
            field=models.CharField(max_length=128, verbose_name='Ссылка'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mainpagecategorybaritem',
            name='order',
            field=models.IntegerField(unique=True, verbose_name='Порядковый номер'),
        ),
        migrations.AlterField(
            model_name='mainpagecategorybaritem',
            name='text',
            field=models.CharField(max_length=100, verbose_name='Текст'),
        ),
        migrations.AlterField(
            model_name='price',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='shop.product', verbose_name='Продукт'),
        ),
    ]
