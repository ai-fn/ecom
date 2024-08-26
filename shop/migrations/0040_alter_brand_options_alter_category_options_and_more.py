# Generated by Django 4.2.11 on 2024-08-26 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0039_alter_productgroup_products'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brand',
            options={'ordering': ('order', 'name', '-created_at'), 'verbose_name': 'Бренд', 'verbose_name_plural': 'Бренды'},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('order', '-created_at'), 'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='characteristic',
            options={'ordering': ('name', '-created_at'), 'verbose_name': 'Характеристика', 'verbose_name_plural': 'Характеристики'},
        ),
        migrations.AlterModelOptions(
            name='characteristicvalue',
            options={'ordering': ('-created_at',), 'verbose_name': 'Значение характеристики для товара', 'verbose_name_plural': 'Значение характеристик для товара'},
        ),
        migrations.AlterModelOptions(
            name='favoriteproduct',
            options={'ordering': ('user', '-created_at'), 'verbose_name': 'Избранный товар', 'verbose_name_plural': 'Избранные товары'},
        ),
        migrations.AlterModelOptions(
            name='footeritem',
            options={'ordering': ('column', 'order', '-created_at'), 'verbose_name': 'Элемент Footer', 'verbose_name_plural': 'Элементы Footer'},
        ),
        migrations.AlterModelOptions(
            name='mainpagecategorybaritem',
            options={'ordering': ('order', '-created_at'), 'verbose_name': 'Категория для панели на главной странице', 'verbose_name_plural': 'Категории для панели на главной странице'},
        ),
        migrations.AlterModelOptions(
            name='mainpagesliderimage',
            options={'ordering': ('order', '-created_at'), 'verbose_name': 'Изображение главной страницы', 'verbose_name_plural': 'Изображения главной страницы'},
        ),
        migrations.AlterModelOptions(
            name='page',
            options={'ordering': ('title', '-created_at'), 'verbose_name': 'Страница', 'verbose_name_plural': 'Страницы'},
        ),
        migrations.AlterModelOptions(
            name='price',
            options={'ordering': ('product', '-created_at'), 'verbose_name': 'Цена', 'verbose_name_plural': 'Цены'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ('-priority', 'title', '-created_at'), 'verbose_name': 'Товар', 'verbose_name_plural': 'Товары'},
        ),
        migrations.AlterModelOptions(
            name='productfile',
            options={'ordering': ('product', 'name', '-created_at'), 'verbose_name': 'Документация', 'verbose_name_plural': 'Документация'},
        ),
        migrations.AlterModelOptions(
            name='productgroup',
            options={'ordering': ('name', '-created_at'), 'verbose_name': 'Грпппа продуктов', 'verbose_name_plural': 'Грпппы продуктов'},
        ),
        migrations.AlterModelOptions(
            name='productimage',
            options={'ordering': ('product', 'name', '-created_at'), 'verbose_name': 'Изображение товара', 'verbose_name_plural': 'Изображения товаров'},
        ),
        migrations.AlterModelOptions(
            name='promo',
            options={'ordering': ('-created_at',), 'verbose_name': 'Акция', 'verbose_name_plural': 'Акции'},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ('product', 'user', '-created_at'), 'verbose_name': 'Отзыв', 'verbose_name_plural': 'Отзывы'},
        ),
        migrations.AlterModelOptions(
            name='searchhistory',
            options={'ordering': ('user', 'title', '-created_at'), 'verbose_name': 'История поиска', 'verbose_name_plural': 'Истории поиска'},
        ),
        migrations.AlterModelOptions(
            name='setting',
            options={'ordering': ('-created_at',), 'verbose_name': 'Настройка', 'verbose_name_plural': 'Настройки'},
        ),
        migrations.AlterModelOptions(
            name='sidebarmenuitem',
            options={'ordering': ('order', '-created_at'), 'verbose_name': 'Элемент бокового меню', 'verbose_name_plural': 'Элементы бокового меню'},
        ),
        migrations.AlterField(
            model_name='brand',
            name='order',
            field=models.BigIntegerField(blank=True, verbose_name='Порядковый номер бренда'),
        ),
        migrations.AlterField(
            model_name='category',
            name='order',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='Порядковый номер категории'),
        ),
        migrations.AlterField(
            model_name='mainpagecategorybaritem',
            name='order',
            field=models.IntegerField(blank=True, verbose_name='Порядковый номер'),
        ),
        migrations.AlterField(
            model_name='sidebarmenuitem',
            name='order',
            field=models.PositiveSmallIntegerField(blank=True, verbose_name='Порядковый номер'),
        ),
    ]
