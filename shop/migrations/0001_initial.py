# Generated by Django 4.2.11 on 2024-06-26 06:48

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(default='Нет имени', max_length=128, verbose_name='Имя бренда')),
                ('icon', models.FileField(blank=True, null=True, upload_to='category_icons/', verbose_name='Иконка')),
                ('slug', models.SlugField(max_length=256, unique=True)),
                ('order', models.BigIntegerField(blank=True, verbose_name='Порядковый номер бренда')),
            ],
            options={
                'verbose_name': 'Бренд',
                'verbose_name_plural': 'Бренды',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('thumb_img', models.TextField(blank=True, max_length=1024, null=True, verbose_name='Миниатюра')),
                ('name', models.CharField(max_length=255, verbose_name='Категория')),
                ('slug', models.SlugField(max_length=256, unique=True)),
                ('icon', models.FileField(blank=True, null=True, upload_to='category_icons/', verbose_name='Иконка')),
                ('image', models.ImageField(blank=True, null=True, upload_to='category/', verbose_name='Изображение')),
                ('is_visible', models.BooleanField(default=True, verbose_name='Видна ли категория (ВЕЗДЕ)')),
                ('is_popular', models.BooleanField(default=False, verbose_name='Популярна ли категория')),
                ('order', models.BigIntegerField(blank=True, verbose_name='Порядковый номер категории')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='shop.category', verbose_name='Каталог')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Characteristic',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('slug', models.SlugField(max_length=256, unique=True, verbose_name='Слаг')),
                ('for_filtering', models.BooleanField(blank=True, default=False, help_text='Будет ли эта характеристика отображаться в фильтрах товаров', verbose_name='Для фильтрации')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='characteristics', to='shop.category', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Характеристика',
                'verbose_name_plural': 'Характеристики',
            },
        ),
        migrations.CreateModel(
            name='MainPageCategoryBarItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(unique=True, verbose_name='Порядковый номер')),
                ('link', models.CharField(max_length=128, verbose_name='Ссылка')),
                ('text', models.CharField(max_length=100, verbose_name='Текст')),
            ],
            options={
                'verbose_name': 'Категория для панели на главной странице',
                'verbose_name_plural': 'Категории для панели на главной странице',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='MainPageSliderImage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('thumb_img', models.TextField(blank=True, max_length=1024, null=True, verbose_name='Миниатюра')),
                ('order', models.IntegerField(unique=True, verbose_name='Порядковый номер')),
                ('link', models.URLField(blank=True, null=True, verbose_name='Ссылка')),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Заголовок')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Описание')),
                ('button_text', models.CharField(blank=True, max_length=100, null=True, verbose_name='Текст на кнопке')),
                ('image', models.ImageField(upload_to='main/sliders/', verbose_name='Изображение')),
            ],
            options={
                'verbose_name': 'Изображение главной страницы',
                'verbose_name_plural': 'Изображения главной страницы',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255, verbose_name='Наименование')),
                ('description', models.TextField(max_length=1024, verbose_name='Описание')),
                ('slug', models.SlugField(unique=True, verbose_name='Слаг страницы')),
                ('image', models.ImageField(blank=True, null=True, upload_to='pages/', verbose_name='Изображение')),
            ],
            options={
                'verbose_name': 'Страница',
                'verbose_name_plural': 'Страницы',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('thumb_img', models.TextField(blank=True, max_length=1024, null=True, verbose_name='Миниатюра')),
                ('title', models.CharField(max_length=255, verbose_name='Наименование')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('catalog_image', models.ImageField(blank=True, max_length=255, null=True, upload_to='catalog/products/images/', verbose_name='Изображение в каталоге')),
                ('search_image', models.ImageField(blank=True, max_length=255, null=True, upload_to='catalog/products/images/', verbose_name='Изображение в поиске')),
                ('original_image', models.ImageField(blank=True, max_length=255, null=True, upload_to='catalog/products/images/', verbose_name='Исходное изображение')),
                ('slug', models.SlugField(max_length=256, unique=True)),
                ('in_stock', models.BooleanField(default=True, verbose_name='В наличии ли товар')),
                ('is_popular', models.BooleanField(default=False, verbose_name='Популярен ли товар')),
                ('is_new', models.BooleanField(default=False, verbose_name='Новый ли товар')),
                ('priority', models.IntegerField(default=500, validators=[django.core.validators.MaxValueValidator(1000000), django.core.validators.MinValueValidator(1)], verbose_name='Приоритет показа')),
                ('article', models.CharField(max_length=128, unique=True, verbose_name='Артикул')),
                ('additional_categories', models.ManyToManyField(blank=True, related_name='additional_products', to='shop.category', verbose_name='Дополнительные категории')),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='shop.brand', verbose_name='Бренд')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='shop.category', verbose_name='Каноническая категория')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товары',
            },
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(choices=[('boolean', 'Boolean'), ('string', 'Строка'), ('number', 'Число')], default='boolean', max_length=50, verbose_name='Тип')),
                ('value_string', models.CharField(blank=True, max_length=255, null=True, verbose_name='Строковое значение')),
                ('value_boolean', models.BooleanField(blank=True, null=True, verbose_name='Логическое значение')),
                ('value_number', models.IntegerField(blank=True, null=True, verbose_name='Числовое значение')),
                ('predefined_key', models.CharField(blank=True, choices=[('maintenance', 'Тех. работы'), ('cdn_enabled', 'Включен ли CDN'), ('cdn_address', 'Адрес CDN'), ('multidomains_enabled', 'Включен ли Multidomains'), ('robots_txt', 'Наполнение для robots.txt')], max_length=255, null=True, verbose_name='Предопределенный ключ')),
                ('custom_key', models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='Пользовательский ключ')),
            ],
            options={
                'verbose_name': 'Настройка',
                'verbose_name_plural': 'Настройки',
            },
        ),
        migrations.CreateModel(
            name='SideBarMenuItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.PositiveSmallIntegerField(default=0, unique=True, verbose_name='Порядковый номер')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('link', models.CharField(max_length=255, verbose_name='Ссылка')),
                ('icon', models.CharField(blank=True, help_text='delivery, documentation, cart, orders, profile, info', max_length=32, null=True, verbose_name='Заголовок иконки')),
            ],
            options={
                'verbose_name': 'Элемент бокового меню',
                'verbose_name_plural': 'Элементы бокового меню',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='SearchHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=128, verbose_name='Заголовок поиска')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'История поиска',
                'verbose_name_plural': 'Истории поиска',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(5)], verbose_name='Рейтинг')),
                ('review', models.TextField(max_length=255, verbose_name='Отзыв')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reviews', to='shop.product', verbose_name='Товар')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Комментатор')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
            },
        ),
        migrations.CreateModel(
            name='Promo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('thumb_img', models.TextField(blank=True, max_length=1024, null=True, verbose_name='Миниатюра')),
                ('name', models.CharField(max_length=64, verbose_name='Название акции')),
                ('image', models.ImageField(upload_to='promo/', verbose_name='Изображение')),
                ('is_active', models.BooleanField(default=False, verbose_name='Активна ли акция')),
                ('active_to', models.DateField(verbose_name='До какого времени акция активна?')),
                ('categories', models.ManyToManyField(blank=True, related_name='promos', to='shop.category', verbose_name='Категории в акции')),
                ('cities', models.ManyToManyField(related_name='promos', to='account.city')),
                ('products', models.ManyToManyField(blank=True, related_name='promos', to='shop.product', verbose_name='Товары в акции')),
            ],
            options={
                'verbose_name': 'Акция',
                'verbose_name_plural': 'Акции',
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('thumb_img', models.TextField(blank=True, max_length=1024, null=True, verbose_name='Миниатюра')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('image', models.ImageField(max_length=255, upload_to='catalog/products/images/', verbose_name='Изображение')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='shop.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Изображение товара',
                'verbose_name_plural': 'Изображения товаров',
            },
        ),
        migrations.CreateModel(
            name='ProductGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Наименование')),
                ('characteristic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.characteristic', verbose_name='Характеристика')),
                ('products', models.ManyToManyField(blank=True, to='shop.product', verbose_name='Продукты')),
            ],
            options={
                'verbose_name': 'Грпппа продуктов',
                'verbose_name_plural': 'Грпппы продуктов',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ProductFrequenlyBoughtTogether',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('purchase_count', models.PositiveBigIntegerField(default=0, verbose_name='Количество покупок')),
                ('product_from', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product_from', to='shop.product', verbose_name='Какой товар')),
                ('product_to', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product_to', to='shop.product', verbose_name='Вместе с каким товаром')),
            ],
            options={
                'verbose_name': 'Часто покупают вместе',
                'verbose_name_plural': 'Часто покупают вместе',
            },
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
        migrations.AddField(
            model_name='product',
            name='frequenly_bought_together',
            field=models.ManyToManyField(blank=True, through='shop.ProductFrequenlyBoughtTogether', to='shop.product', verbose_name='Часто покупают вместе с'),
        ),
        migrations.AddField(
            model_name='product',
            name='similar_products',
            field=models.ManyToManyField(blank=True, to='shop.product', verbose_name='Похожие продукты'),
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('old_price', models.DecimalField(decimal_places=2, max_digits=10, null=True, verbose_name='Старая цена (для скидки)')),
                ('city_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='account.citygroup', verbose_name='Группа городов')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='shop.product', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Цена',
                'verbose_name_plural': 'Цены',
            },
        ),
        migrations.CreateModel(
            name='OpenGraphMeta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('description', models.TextField(max_length=1024, verbose_name='Описание')),
                ('url', models.CharField(max_length=255, verbose_name='Ссылка')),
                ('site_name', models.CharField(default='Кров маркет', max_length=255, verbose_name='Наименование сайта')),
                ('locale', models.CharField(blank=True, default='ru_RU', help_text='В формате ru_Ru', max_length=10, null=True, verbose_name='Языковой код')),
                ('object_id', models.PositiveIntegerField(verbose_name='ID объекта')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='Тип объекта')),
            ],
            options={
                'verbose_name': 'Метаданные',
                'verbose_name_plural': 'Метаданные',
            },
        ),
        migrations.CreateModel(
            name='ImageMetaData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(upload_to='pages/', verbose_name='Изображение')),
                ('width', models.PositiveSmallIntegerField(verbose_name='Ширина')),
                ('height', models.PositiveSmallIntegerField(verbose_name='Высота')),
                ('open_graph_meta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.opengraphmeta', verbose_name='Метаданные')),
            ],
            options={
                'verbose_name': 'Изображение метаданных',
                'verbose_name_plural': 'Изображения метаданных',
            },
        ),
        migrations.CreateModel(
            name='FooterItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('column', models.PositiveSmallIntegerField(verbose_name='Номер колонки')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядковый номер')),
                ('title', models.CharField(max_length=100, verbose_name='Наименование')),
                ('link', models.CharField(default='#', verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': 'Элемент Footer',
                'verbose_name_plural': 'Элементы Footer',
                'ordering': ['order'],
                'unique_together': {('column', 'order')},
            },
        ),
        migrations.CreateModel(
            name='FavoriteProduct',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='shop.product', verbose_name='Товар')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_products', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Избранный товар',
                'verbose_name_plural': 'Избранные товары',
            },
        ),
        migrations.CreateModel(
            name='CharacteristicValue',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('value', models.CharField(max_length=1024, verbose_name='Значение')),
                ('slug', models.SlugField(max_length=1024, verbose_name='Слаг')),
                ('characteristic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.characteristic', verbose_name='Характеристика')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='characteristic_values', to='shop.product', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Значение характеристики для товара',
                'verbose_name_plural': 'Значение характеристик для товара',
            },
        ),
        migrations.CreateModel(
            name='CategoryMetaData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=128, null=True, verbose_name='Title')),
                ('description', models.CharField(max_length=128, null=True, verbose_name='Описание')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_meta', to='shop.category')),
            ],
            options={
                'verbose_name': 'Метаданные категории',
                'verbose_name_plural': 'Метаданные категорий',
            },
        ),
        migrations.AddIndex(
            model_name='brand',
            index=models.Index(fields=['name'], name='shop_brand_name_c466ec_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='searchhistory',
            unique_together={('title', 'user')},
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['product'], name='shop_review_product_d2a5c4_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['rating'], name='shop_review_rating_0c1338_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='productfrequenlyboughttogether',
            unique_together={('product_from', 'product_to')},
        ),
        migrations.AlterUniqueTogether(
            name='productfile',
            unique_together={('product', 'name')},
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['title'], name='shop_produc_title_4a03b1_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['slug'], name='shop_produc_slug_76971b_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category'], name='shop_produc_categor_d249e3_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['article'], name='shop_produc_article_6c9444_idx'),
        ),
        migrations.AddIndex(
            model_name='price',
            index=models.Index(fields=['product', 'city_group'], name='shop_price_product_ed0f7b_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='price',
            unique_together={('product', 'city_group')},
        ),
        migrations.AlterUniqueTogether(
            name='favoriteproduct',
            unique_together={('user', 'product')},
        ),
        migrations.AlterUniqueTogether(
            name='characteristicvalue',
            unique_together={('characteristic', 'product', 'slug')},
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['name'], name='shop_catego_name_289c7e_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['slug'], name='shop_catego_slug_5ac49f_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['parent'], name='shop_catego_parent__bb774a_idx'),
        ),
    ]
