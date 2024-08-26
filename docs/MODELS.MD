# Shop App Models

# Models Documentation

## ThumbModel

| Field      | Type          | Options                                | Description |
| ---------- | ------------- | -------------------------------------- | ----------- |
| id         | AutoField     | primary_key=True                       | Primary Key |
| created_at | DateTimeField | auto_now_add=True                      | Created At  |
| updated_at | DateTimeField | auto_now=True                          | Updated At  |
| thumb_img  | TextField     | null=True, blank=True, max_length=1024 | Миниатюра   |

## Category

| Field              | Type            | Options                                                                          | Description                |
| ------------------ | --------------- | -------------------------------------------------------------------------------- | -------------------------- |
| id                 | AutoField       | primary_key=True                                                                 | Primary Key                |
| created_at         | DateTimeField   | auto_now_add=True                                                                | Created At                 |
| updated_at         | DateTimeField   | auto_now=True                                                                    | Updated At                 |
| name               | CharField       | max_length=255                                                                   | Категория                  |
| slug               | SlugField       | unique=True, max_length=256                                                      |                            |
| parent             | TreeForeignKey  | "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children" | Каталог                    |
| icon               | FileField       | upload_to="category_icons/", null=True, blank=True                               | Иконка                     |
| image              | ImageField      | upload_to="category/", null=True, blank=True                                     | Изображение                |
| is_visible         | BooleanField    | default=True                                                                     | Видна ли категория (ВЕЗДЕ) |
| is_popular         | BooleanField    | default=False                                                                    | Популярна ли категория     |
| order              | BigIntegerField | blank=True                                                                       | Порядковый номер категории |
| opengraph_metadata | GenericRelation | "OpenGraphMeta", related_query_name="category"                                   |                            |
| thumb_img          | TextField       | null=True, blank=True, max_length=1024                                           | Миниатюра                  |

**Methods**

| Method           | Description                                                    |
| ---------------- | -------------------------------------------------------------- |
| get_absolute_url | Returns the absolute URL of the category.                      |
| __str__          | Returns the name of the category as its string representation. |
| clean            | Validates that only root categories can have images.           |

**Meta Options**

| Option              | Value                      |
| ------------------- | -------------------------- |
| verbose_name        | Категория                  |
| verbose_name_plural | Категории                  |
| ordering            | ("-id",)                   |
| indexes             | ["name", "slug", "parent"] |

**MPTTMeta Options**

| Option             | Value    |
| ------------------ | -------- |
| order_insertion_by | ["name"] |

## HTMLMetaTags

| Field          | Type                 | Options                                                 | Description                      |
| -------------- | -------------------- | ------------------------------------------------------- | -------------------------------- |
| id             | AutoField            | primary_key=True                                        | Primary Key                      |
| created_at     | DateTimeField        | auto_now_add=True                                       | Created At                       |
| updated_at     | DateTimeField        | auto_now=True                                           | Updated At                       |
| title          | CharField            | max_length=1024                                         | Заголовок                        |
| description    | TextField            | max_length=4096                                         | Описание                         |
| keywords       | TextField            | max_length=4096                                         | Ключевые слова                   |
| content_type   | ForeignKey           | on_delete=models.CASCADE, verbose_name=_("Тип объекта") | Тип объекта                      |
| object_id      | PositiveIntegerField | verbose_name=_("Уникальный идентификатор объекта")      | Уникальный идентификатор объекта |
| content_object | GenericForeignKey    | "content_type", "object_id"                             |                                  |
| thumb_img      | TextField            | null=True, blank=True, max_length=1024                  | Миниатюра                        |

**Methods**

| Method                 | Description                                      |
| ---------------------- | ------------------------------------------------ |
| get_formatted_meta_tag | Returns formatted meta tag based on city domain. |

**Meta Options**

| Option              | Value                 |
| ------------------- | --------------------- |
| verbose_name        | Тег метаданных        |
| verbose_name_plural | Теги метаданных       |
| ordering            | ("-created_at", "id") |

## Brand

| Field      | Type            | Options                                            | Description             |
| ---------- | --------------- | -------------------------------------------------- | ----------------------- |
| id         | AutoField       | primary_key=True                                   | Primary Key             |
| created_at | DateTimeField   | auto_now_add=True                                  | Created At              |
| updated_at | DateTimeField   | auto_now=True                                      | Updated At              |
| name       | CharField       | max_length=128, default="Нет имени"                | Имя бренда              |
| icon       | FileField       | upload_to="category_icons/", null=True, blank=True | Иконка                  |
| slug       | SlugField       | unique=True, max_length=256                        |                         |
| order      | BigIntegerField | blank=True                                         | Порядковый номер бренда |

**Methods**

| Method  | Description                                                 |
| ------- | ----------------------------------------------------------- |
| __str__ | Returns the name of the brand as its string representation. |

**Meta Options**

| Option              | Value    |
| ------------------- | -------- |
| verbose_name        | Бренд    |
| verbose_name_plural | Бренды   |
| indexes             | ["name"] |

## Product

| Field                     | Type            | Options                                                                         | Description              |
| ------------------------- | --------------- | ------------------------------------------------------------------------------- | ------------------------ |
| id                        | AutoField       | primary_key=True                                                                | Primary Key              |
| created_at                | DateTimeField   | auto_now_add=True                                                               | Created At               |
| updated_at                | DateTimeField   | auto_now=True                                                                   | Updated At               |
| category                  | ForeignKey      | Category, on_delete=models.PROTECT, related_name="products"                     | Каноническая категория   |
| additional_categories     | ManyToManyField | Category, related_name="additional_products", blank=True                        | Дополнительные категории |
| brand                     | ForeignKey      | Brand, on_delete=models.PROTECT, related_name="products", null=True, blank=True | Бренд                    |
| title                     | CharField       | max_length=255                                                                  | Наименование             |
| description               | TextField       | null=True, blank=True                                                           | Описание                 |
| catalog_image             | ImageField      | upload_to="catalog/products/images/", null=True, blank=True, max_length=255     | Изображение в каталоге   |
| search_image              | ImageField      | upload_to="catalog/products/images/", null=True, blank=True, max_length=255     | Изображение в поиске     |
| original_image            | ImageField      | upload_to="catalog/products/images/", null=True, blank=True, max_length=255     | Исходное изображение     |
| slug                      | SlugField       | unique=True, max_length=256                                                     |                          |
| similar_products          | ManyToManyField | "self", blank=True                                                              | Похожие продукты         |
| in_stock                  | BooleanField    | default=True                                                                    | В наличии ли товар       |
| is_popular                | BooleanField    | default=False                                                                   | Популярен ли товар       |
| is_new                    | BooleanField    | default=False, verbose_name=_("Новый ли товар")                                 | Новый ли товар           |
| priority                  | IntegerField    | default=500, validators=[MaxValueValidator(10**6), MinValueValidator(1)]        | Приоритет показа         |
| frequenly_bought_together | ManyToManyField | "self", through="ProductFrequenlyBoughtTogether", blank=True                    | Часто покупают вместе с  |
| article                   | CharField       | max_length=128, unique=True                                                     | Артикул                  |
| unavailable_in            | ManyToManyField | City, related_query_name="product", blank=True                                  | Недоступен в городах     |
| opengraph_metadata        | GenericRelation | "OpenGraphMeta", related_query_name="product"                                   |                          |
| thumb_img                 | TextField       | null=True, blank=True, max_length=1024                                          | Миниатюра                |

**Methods**

| Method           | Description                                                   |
| ---------------- | ------------------------------------------------------------- |
| get_absolute_url | Returns the absolute URL of the product.                      |
| __str__          | Returns the name of the product as its string representation. |

**Meta Options**

| Option              | Value                                    |
| ------------------- | ---------------------------------------- |
| verbose_name        | Товар                                    |
| verbose_name_plural | Товары                                   |
| indexes             | ["title", "slug", "category", "article"] |

## FavoriteProduct

| Field      | Type          | Options                                                                | Description  |
| ---------- | ------------- | ---------------------------------------------------------------------- | ------------ |
| id         | AutoField     | primary_key=True                                                       | Primary Key  |
| created_at | DateTimeField | auto_now_add=True                                                      | Created At   |
| updated_at | DateTimeField | auto_now=True                                                          | Updated At   |
| user       | ForeignKey    | CustomUser, on_delete=models.CASCADE, related_name="favorite_products" | Пользователь |
| product    | ForeignKey    | Product, on_delete=models.CASCADE, related_name="favorited_by"         | Товар        |

**Methods**

| Method  | Description                                              |
| ------- | -------------------------------------------------------- |
| __str__ | Returns a string representation of the favorite product. |

**Meta Options**

| Option              | Value               |
| ------------------- | ------------------- |
| unique_together     | ("user", "product") |
| verbose_name        | Избранный товар     |
| verbose_name_plural | Избранные товары    |

## ProductFile

| Field      | Type          | Options                                                 | Description  |
| ---------- | ------------- | ------------------------------------------------------- | ------------ |
| id         | AutoField     | primary_key=True                                        | Primary Key  |
| created_at | DateTimeField | auto_now_add=True                                       | Created At   |
| updated_at | DateTimeField | auto_now=True                                           | Updated At   |
| product    | ForeignKey    | Product, on_delete=models.CASCADE, related_name="files" | Продукт      |
| name       | CharField     | max_length=512                                          | Наименование |
| file       | FileField     | max_length=512, upload_to="catalog/products/documents/" | Файл         |

**Meta Options**

| Option              | Value               |
| ------------------- | ------------------- |
| unique_together     | ("product", "name") |
| verbose_name        | Документация        |
| verbose_name_plural | Документация        |

## ProductFrequenlyBoughtTogether

| Field          | Type                    | Options                                                        | Description            |
| -------------- | ----------------------- | -------------------------------------------------------------- | ---------------------- |
| id             | AutoField               | primary_key=True                                               | Primary Key            |
| created_at     | DateTimeField           | auto_now_add=True                                              | Created At             |
| updated_at     | DateTimeField           | auto_now=True                                                  | Updated At             |
| product_from   | ForeignKey              | Product, on_delete=models.PROTECT, related_name="product_from" | Какой товар            |
| product_to     | ForeignKey              | Product, on_delete=models.PROTECT, related_name="product_to"   | Вместе с каким товаром |
| purchase_count | PositiveBigIntegerField | default=0                                                      | Количество покупок     |

**Meta Options**

| Option              | Value                          |
| ------------------- | ------------------------------ |
| unique_together     | ("product_from", "product_to") |
| verbose_name        | Часто покупают вместе          |
| verbose_name_plural | Часто покупают вместе          |

## ProductImage

| Field      | Type          | Options                                                  | Description |
| ---------- | ------------- | -------------------------------------------------------- | ----------- |
| id         | AutoField     | primary_key=True                                         | Primary Key |
| created_at | DateTimeField | auto_now_add=True                                        | Created At  |
| updated_at | DateTimeField | auto_now=True                                            | Updated At  |
| product    | ForeignKey    | Product, on_delete=models.CASCADE, related_name="images" | Товар       |
| name       | CharField     | max_length=255                                           | Название    |
| image      | ImageField    | upload_to="catalog/products/images/", max_length=255     | Изображение |

**Methods**

| Method  | Description                                           |
| ------- | ----------------------------------------------------- |
| __str__ | Returns a string representation of the product image. |

**Meta Options**

| Option              | Value               |
| ------------------- | ------------------- |
| verbose_name        | Изображение товара  |
| verbose_name_plural | Изображения товаров |

## Promo

| Field      | Type            | Options                                     | Description                      |
| ---------- | --------------- | ------------------------------------------- | -------------------------------- |
| id         | AutoField       | primary_key=True                            | Primary Key                      |
| created_at | DateTimeField   | auto_now_add=True                           | Created At                       |
| updated_at | DateTimeField   | auto_now=True                               | Updated At                       |
| name       | CharField       | max_length=64                               | Название акции                   |
| categories | ManyToManyField | Category, related_name="promos", blank=True | Категории в акции                |
| products   | ManyToManyField | Product, related_name="promos", blank=True  | Товары в акции                   |
| image      | ImageField      | upload_to="promo/"                          | Изображение                      |
| cities     | ManyToManyField | City, related_name="promos"                 |                                  |
| is_active  | BooleanField    | default=False                               | Активна ли акция                 |
| active_to  | DateField       |                                             | До какого времени акция активна? |
| thumb_img  | TextField       | null=True, blank=True, max_length=1024      | Миниатюра                        |

**Methods**

| Method  | Description                                                 |
| ------- | ----------------------------------------------------------- |
| __str__ | Returns the name of the promo as its string representation. |

**Meta Options**

| Option              | Value |
| ------------------- | ----- |
| verbose_name        | Акция |
| verbose_name_plural | Акции |


## Characteristic

| Field         | Type          | Options                                                                                                    | Description    |
| ------------- | ------------- | ---------------------------------------------------------------------------------------------------------- | -------------- |
| id            | AutoField     | primary_key=True                                                                                           | Primary Key    |
| created_at    | DateTimeField | auto_now_add=True                                                                                          | Created At     |
| updated_at    | DateTimeField | auto_now=True                                                                                              | Updated At     |
| name          | CharField     | max_length=255                                                                                             | Наименование   |
| slug          | SlugField     | unique=True, max_length=256                                                                                | Слаг           |
| category      | ForeignKey    | Category, related_name="characteristics", on_delete=models.CASCADE, null=True, verbose_name=_("Категория") | Категория      |
| for_filtering | BooleanField  | default=False, blank=True, help_text=_("Будет ли эта характеристика отображаться в фильтрах товаров")      | Для фильтрации |

**Methods**

| Method  | Description                             |
| ------- | --------------------------------------- |
| __str__ | Returns the name of the characteristic. |

**Meta Options**

| Option              | Value          |
| ------------------- | -------------- |
| verbose_name        | Характеристика |
| verbose_name_plural | Характеристики |

## CharacteristicValue

| Field          | Type          | Options                                                                 | Description    |
| -------------- | ------------- | ----------------------------------------------------------------------- | -------------- |
| id             | AutoField     | primary_key=True                                                        | Primary Key    |
| created_at     | DateTimeField | auto_now_add=True                                                       | Created At     |
| updated_at     | DateTimeField | auto_now=True                                                           | Updated At     |
| product        | ForeignKey    | Product, related_name="characteristic_values", on_delete=models.CASCADE | Продукт        |
| characteristic | ForeignKey    | Characteristic, on_delete=models.CASCADE                                | Характеристика |
| value          | CharField     | max_length=1024                                                         | Значение       |
| slug           | SlugField     | max_length=1024                                                         | Слаг           |

**Methods**

| Method  | Description                                                    |
| ------- | -------------------------------------------------------------- |
| __str__ | Returns a formatted string with characteristic name and value. |

**Meta Options**

| Option              | Value                                 |
| ------------------- | ------------------------------------- |
| verbose_name        | Значение характеристики для товара    |
| verbose_name_plural | Значение характеристик для товара     |
| unique_together     | ("characteristic", "product", "slug") |

## Review

| Field      | Type                      | Options                                                       | Description |
| ---------- | ------------------------- | ------------------------------------------------------------- | ----------- |
| id         | AutoField                 | primary_key=True                                              | Primary Key |
| created_at | DateTimeField             | auto_now_add=True                                             | Created At  |
| updated_at | DateTimeField             | auto_now=True                                                 | Updated At  |
| product    | ForeignKey                | Product, related_name="reviews", on_delete=models.PROTECT     | Товар       |
| user       | ForeignKey                | CustomUser, related_name="comments", on_delete=models.PROTECT | Комментатор |
| rating     | PositiveSmallIntegerField | validators=[MaxValueValidator(5)]                             | Рейтинг     |
| review     | TextField                 | max_length=255                                                | Отзыв       |

**Methods**

| Method  | Description                                                 |
| ------- | ----------------------------------------------------------- |
| __str__ | Returns a formatted string with user's last and first name. |

**Meta Options**

| Option              | Value                 |
| ------------------- | --------------------- |
| verbose_name        | Отзыв                 |
| verbose_name_plural | Отзывы                |
| indexes             | ["product", "rating"] |

## Price

| Field      | Type          | Options                                                    | Description              |
| ---------- | ------------- | ---------------------------------------------------------- | ------------------------ |
| id         | AutoField     | primary_key=True                                           | Primary Key              |
| created_at | DateTimeField | auto_now_add=True                                          | Created At               |
| updated_at | DateTimeField | auto_now=True                                              | Updated At               |
| product    | ForeignKey    | Product, related_name="prices", on_delete=models.CASCADE   | Продукт                  |
| city_group | ForeignKey    | CityGroup, related_name="prices", on_delete=models.CASCADE | Группа городов           |
| price      | DecimalField  | max_digits=10, decimal_places=2                            | Цена                     |
| old_price  | DecimalField  | max_digits=10, decimal_places=2, null=True                 | Старая цена (для скидки) |

**Methods**

| Method  | Description                                                                |
| ------- | -------------------------------------------------------------------------- |
| __str__ | Returns a formatted string with product title, city group name, and price. |

**Meta Options**

| Option              | Value                     |
| ------------------- | ------------------------- |
| verbose_name        | Цена                      |
| verbose_name_plural | Цены                      |
| unique_together     | ("product", "city_group") |
| indexes             | ["product", "city_group"] |

## Setting

| Field          | Type          | Options                                                               | Description           |
| -------------- | ------------- | --------------------------------------------------------------------- | --------------------- |
| id             | AutoField     | primary_key=True                                                      | Primary Key           |
| created_at     | DateTimeField | auto_now_add=True                                                     | Created At            |
| updated_at     | DateTimeField | auto_now=True                                                         | Updated At            |
| type           | CharField     | max_length=50, default=SettingsTypeChoices.BOOLEAN                    | Тип                   |
| value_string   | CharField     | max_length=255, null=True, blank=True                                 | Строковое значение    |
| value_boolean  | BooleanField  | null=True, blank=True                                                 | Логическое значение   |
| value_number   | IntegerField  | null=True, blank=True                                                 | Числовое значение     |
| predefined_key | CharField     | max_length=255, null=True, blank=True, choices=SettingChoices.choices | Предопределенный ключ |
| custom_key     | CharField     | max_length=255, null=True, blank=True, unique=True                    | Пользовательский ключ |

**Methods**

| Method    | Description                                                    |
| --------- | -------------------------------------------------------------- |
| clean     | Validates the presence of either predefined_key or custom_key. |
| get_value | Returns the value based on the type.                           |
| save      | Cleans and saves the setting.                                  |
| get_key   | Returns the predefined_key or custom_key.                      |
| __str__   | Returns a formatted string with key and value.                 |

**Meta Options**

| Option              | Value     |
| ------------------- | --------- |
| verbose_name        | Настройка |
| verbose_name_plural | Настройки |

## FooterItem

| Field      | Type                      | Options                              | Description      |
| ---------- | ------------------------- | ------------------------------------ | ---------------- |
| id         | AutoField                 | primary_key=True                     | Primary Key      |
| created_at | DateTimeField             | auto_now_add=True                    | Created At       |
| updated_at | DateTimeField             | auto_now=True                        | Updated At       |
| column     | PositiveSmallIntegerField |                                      | Номер колонки    |
| order      | PositiveIntegerField      | default=0                            | Порядковый номер |
| title      | CharField                 | max_length=100                       | Наименование     |
| link       | CharField                 | default="#", blank=False, null=False | Ссылка           |

**Methods**

| Method  | Description                                   |
| ------- | --------------------------------------------- |
| __str__ | Returns a formatted string with title and id. |

**Meta Options**

| Option              | Value               |
| ------------------- | ------------------- |
| verbose_name        | Элемент Footer      |
| verbose_name_plural | Элементы Footer     |
| ordering            | ["order"]           |
| unique_together     | ("column", "order") |


## MainPageSliderImage

| Field       | Type          | Options                                  | Description           |
| ----------- | ------------- | ---------------------------------------- | --------------------- |
| id          | AutoField     | primary_key=True                         | Primary Key           |
| created_at  | DateTimeField | auto_now_add=True                        | Created At            |
| updated_at  | DateTimeField | auto_now=True                            | Updated At            |
| order       | IntegerField  | unique=True                              | Порядковый номер      |
| link        | URLField      | blank=True, null=True                    | Ссылка                |
| title       | CharField     | max_length=255, blank=True, null=True    | Заголовок             |
| description | TextField     | max_length=1024, blank=True, null=True   | Описание              |
| button_text | CharField     | max_length=100, blank=True, null=True    | Текст на кнопке       |
| image       | ImageField    | upload_to="main/sliders/"                | Изображение           |
| tiny_image  | ImageField    | upload_to="main/sliders/tiny", null=True | Маленькое изображение |
| thumb_img   | TextField     | null=True, blank=True, max_length=1024   | Миниатюра             |

**Methods**

| Method  | Description                         |
| ------- | ----------------------------------- |
| __str__ | Returns a formatted string with id. |

**Meta Options**

| Option              | Value                        |
| ------------------- | ---------------------------- |
| verbose_name        | Изображение главной страницы |
| verbose_name_plural | Изображения главной страницы |
| ordering            | ["order"]                    |

## MainPageCategoryBarItem

| Field      | Type          | Options           | Description      |
| ---------- | ------------- | ----------------- | ---------------- |
| id         | AutoField     | primary_key=True  | Primary Key      |
| created_at | DateTimeField | auto_now_add=True | Created At       |
| updated_at | DateTimeField | auto_now=True     | Updated At       |
| order      | IntegerField  | unique=True       | Порядковый номер |
| link       | CharField     | max_length=128    | Ссылка           |
| text       | CharField     | max_length=100    | Текст            |

**Methods**

| Method  | Description                         |
| ------- | ----------------------------------- |
| __str__ | Returns a formatted string with id. |

**Meta Options**

| Option              | Value                                    |
| ------------------- | ---------------------------------------- |
| verbose_name        | Категория для панели на главной странице |
| verbose_name_plural | Категории для панели на главной странице |
| ordering            | ["order"]                                |

## SideBarMenuItem

| Field      | Type                      | Options                                                                                                   | Description      |
| ---------- | ------------------------- | --------------------------------------------------------------------------------------------------------- | ---------------- |
| id         | AutoField                 | primary_key=True                                                                                          | Primary Key      |
| created_at | DateTimeField             | auto_now_add=True                                                                                         | Created At       |
| updated_at | DateTimeField             | auto_now=True                                                                                             | Updated At       |
| order      | PositiveSmallIntegerField | default=0, unique=True                                                                                    | Порядковый номер |
| title      | CharField                 | max_length=100                                                                                            | Заголовок        |
| link       | CharField                 | max_length=255                                                                                            | Ссылка           |
| icon       | CharField                 | max_length=32, null=True, blank=True, help_text=_("delivery, documentation, cart, orders, profile, info") | Заголовок иконки |

**Methods**

| Method  | Description                         |
| ------- | ----------------------------------- |
| __str__ | Returns a formatted string with id. |

**Meta Options**

| Option              | Value                  |
| ------------------- | ---------------------- |
| verbose_name        | Элемент бокового меню  |
| verbose_name_plural | Элементы бокового меню |
| ordering            | ["order"]              |

## ProductGroup

| Field          | Type            | Options                                                          | Description    |
| -------------- | --------------- | ---------------------------------------------------------------- | -------------- |
| id             | AutoField       | primary_key=True                                                 | Primary Key    |
| created_at     | DateTimeField   | auto_now_add=True                                                | Created At     |
| updated_at     | DateTimeField   | auto_now=True                                                    | Updated At     |
| name           | CharField       | max_length=255, unique=True                                      | Наименование   |
| products       | ManyToManyField | Product, blank=True                                              | Продукты       |
| characteristic | ForeignKey      | Characteristic, null=True, blank=True, on_delete=models.SET_NULL | Характеристика |

**Methods**

| Method  | Description                            |
| ------- | -------------------------------------- |
| __str__ | Returns the name of the product group. |

**Meta Options**

| Option              | Value            |
| ------------------- | ---------------- |
| verbose_name        | Грпппа продуктов |
| verbose_name_plural | Грпппы продуктов |
| ordering            | ["name"]         |

## OpenGraphMeta

| Field          | Type                 | Options                                                                               | Description        |
| -------------- | -------------------- | ------------------------------------------------------------------------------------- | ------------------ |
| id             | AutoField            | primary_key=True                                                                      | Primary Key        |
| created_at     | DateTimeField        | auto_now_add=True                                                                     | Created At         |
| updated_at     | DateTimeField        | auto_now=True                                                                         | Updated At         |
| title          | CharField            | max_length=255                                                                        | Заголовок          |
| description    | TextField            | max_length=1024                                                                       | Описание           |
| url            | CharField            | max_length=255                                                                        | Ссылка             |
| site_name      | CharField            | max_length=255, default="Кров маркет"                                                 | Наименование сайта |
| locale         | CharField            | max_length=10, default="ru_RU", null=True, blank=True, help_text=_("В формате ru_Ru") | Языковой код       |
| content_type   | ForeignKey           | ContentType, on_delete=models.CASCADE                                                 | Тип объекта        |
| object_id      | PositiveIntegerField |                                                                                       | ID объекта         |
| content_object | GenericForeignKey    | "content_type", "object_id"                                                           |                    |

**Methods**

| Method  | Description                                     |
| ------- | ----------------------------------------------- |
| __str__ | Returns a formatted string with content object. |

**Meta Options**

| Option              | Value      |
| ------------------- | ---------- |
| verbose_name        | Метаданные |
| verbose_name_plural | Метаданные |


**Methods**

| Method  | Description                         |
| ------- | ----------------------------------- |
| __str__ | Returns a formatted string with id. |

**Meta Options**

| Option              | Value                  |
| ------------------- | ---------------------- |
| verbose_name        | Изображение метаданных |
| verbose_name_plural | Изображения метаданных |

## Page

| Field              | Type            | Options                                   | Description   |
| ------------------ | --------------- | ----------------------------------------- | ------------- |
| id                 | AutoField       | primary_key=True                          | Primary Key   |
| created_at         | DateTimeField   | auto_now_add=True                         | Created At    |
| updated_at         | DateTimeField   | auto_now=True                             | Updated At    |
| title              | CharField       | max_length=255                            | Наименование  |
| description        | TextField       | max_length=1024                           | Описание      |
| slug               | SlugField       | unique=True                               | Слаг страницы |
| image              | ImageField      | upload_to="pages/", blank=True, null=True | Изображение   |
| opengraph_metadata | GenericRelation | OpenGraphMeta, related_query_name="page"  |               |

**Methods**

| Method           | Description                            |
| ---------------- | -------------------------------------- |
| __str__          | Returns a formatted string with title. |
| get_absolute_url | Returns the slug of the page.          |

**Meta Options**

| Option              | Value    |
| ------------------- | -------- |
| verbose_name        | Страница |
| verbose_name_plural | Страницы |

## SearchHistory

| Field      | Type          | Options                              | Description      |
| ---------- | ------------- | ------------------------------------ | ---------------- |
| id         | AutoField     | primary_key=True                     | Primary Key      |
| created_at | DateTimeField | auto_now_add=True                    | Created At       |
| updated_at | DateTimeField | auto_now=True                        | Updated At       |
| title      | CharField     | max_length=128                       | Заголовок поиска |
| user       | ForeignKey    | CustomUser, on_delete=models.CASCADE | Пользователь     |

**Methods**

| Method  | Description                                     |
| ------- | ----------------------------------------------- |
| __str__ | Returns a formatted string with title and user. |

**Meta Options**

| Option              | Value             |
| ------------------- | ----------------- |
| verbose_name        | История поиска    |
| verbose_name_plural | Истории поиска    |
| ordering            | ["-created_at"]   |
| unique_together     | ("title", "user") |

# Cart App Models

## Order

| Field      | Type            | Options                                                                                                   | Description   |
| ---------- | --------------- | --------------------------------------------------------------------------------------------------------- | ------------- |
| id         | AutoField       | primary_key=True                                                                                          | Primary Key   |
| created_at | DateTimeField   | auto_now_add=True                                                                                         | Created At    |
| updated_at | DateTimeField   | auto_now=True                                                                                             | Updated At    |
| customer   | ForeignKey      | CustomUser, related_name="customer", on_delete=models.PROTECT                                             | Покупатель    |
| products   | ManyToManyField | Product, verbose_name="Товары", blank=True, through="ProductsInOrder"                                     | Товары        |
| total      | DecimalField    | max_digits=10, decimal_places=2                                                                           | Сумма заказа  |
| address    | CharField       | max_length=1024                                                                                           | Адрес         |
| status     | CharField       | choices=OrderStatus.choices, verbose_name=_("Статус заказа"), default=OrderStatus.PENDING, max_length=20  | Статус заказа |

**Methods**

| Method  | Description                                                  |
| ------- | ------------------------------------------------------------ |
| __str__ | Returns a formatted string with the customer and created_at. |

**Meta Options**

| Option              | Value  |
| ------------------- | ------ |
| verbose_name        | Заказ  |
| verbose_name_plural | Заказы |

## ProductsInOrder

| Field      | Type                      | Options                                                          | Description                  |
| ---------- | ------------------------- | ---------------------------------------------------------------- | ---------------------------- |
| id         | AutoField                 | primary_key=True                                                 | Primary Key                  |
| created_at | DateTimeField             | auto_now_add=True                                                | Created At                   |
| updated_at | DateTimeField             | auto_now=True                                                    | Updated At                   |
| order      | ForeignKey                | Order, on_delete=models.CASCADE                                  | Заказ                        |
| product    | ForeignKey                | Product, on_delete=models.PROTECT, related_name="count_in_order" | Товар                        |
| quantity   | PositiveSmallIntegerField |                                                                  | Количество товара в заказе   |
| price      | DecimalField              | max_digits=10, decimal_places=2                                  | Цена товара на момент заказа |

**Methods**

| Method  | Description                                    |
| ------- | ---------------------------------------------- |
| __str__ | Returns a formatted string with the basket id. |

**Meta Options**

| Option              | Value             |
| ------------------- | ----------------- |
| verbose_name        | Продукт в заказе  |
| verbose_name_plural | Продукты в заказе |

## CartItem

| Field      | Type                 | Options                                                      | Description |
| ---------- | -------------------- | ------------------------------------------------------------ | ----------- |
| id         | AutoField            | primary_key=True                                             | Primary Key |
| created_at | DateTimeField        | auto_now_add=True                                            | Created At  |
| updated_at | DateTimeField        | auto_now=True                                                | Updated At  |
| customer   | ForeignKey           | CustomUser, related_name="cart", on_delete=models.CASCADE    | Покупатель  |
| product    | ForeignKey           | Product, on_delete=models.CASCADE, related_name="cart_items" | Товар       |
| quantity   | PositiveIntegerField |                                                              | Количество  |

**Methods**

| Method  | Description                                                      |
| ------- | ---------------------------------------------------------------- |
| __str__ | Returns a formatted string with the customer's name and product. |

**Meta Options**

| Option              | Value                           |
| ------------------- | ------------------------------- |
| verbose_name        | Продукт в корзине пользователя  |
| verbose_name_plural | Продукты в корзине пользователя |
| unique_together     | ("customer", "product")         |

# Account App Models

## City

| Field              | Type                    | Options                                                                           | Description            |
| ------------------ | ----------------------- | --------------------------------------------------------------------------------- | ---------------------- |
| id                 | AutoField               | primary_key=True                                                                  | Primary Key            |
| created_at         | DateTimeField           | auto_now_add=True                                                                 | Created At             |
| updated_at         | DateTimeField           | auto_now=True                                                                     | Updated At             |
| is_active          | BooleanField            | default=True                                                                      | Активность             |
| name               | CharField               | max_length=255, unique=True, null=True                                            | Город                  |
| domain             | CharField               | max_length=255, unique=True, null=True                                            | Домен                  |
| address            | CharField               | max_length=256, null=True, blank=True                                             | Адрес                  |
| number             | BigIntegerField         | default=0                                                                         | Номер телефона         |
| how_to_get_office  | CharField               | max_length=512, null=True, blank=True                                             | Как добраться до офиса |
| schedule           | TextField               | default="Отсутствует"                                                             | График работы          |
| population         | PositiveBigIntegerField | default=0                                                                         | Численность населения  |
| city_group         | ForeignKey              | CityGroup, on_delete=models.PROTECT, related_name="cities", null=True, blank=True | Группа городов         |

**Methods**

| Method           | Description                                           |
| ---------------- | ----------------------------------------------------- |
| __str__          | Returns the name of the city.                         |
| get_default_city | Returns the default city or creates it if not exists. |

**Meta Options**

| Option              | Value                         |
| ------------------- | ----------------------------- |
| verbose_name        | Город                         |
| verbose_name_plural | Города                        |
| ordering            | ["name"]                      |
| indexes             | ["name", "domain", "address"] |

## CityGroup

| Field      | Type          | Options                                                                              | Description     |
| ---------- | ------------- | ------------------------------------------------------------------------------------ | --------------- |
| id         | AutoField     | primary_key=True                                                                     | Primary Key     |
| created_at | DateTimeField | auto_now_add=True                                                                    | Created At      |
| updated_at | DateTimeField | auto_now=True                                                                        | Updated At      |
| is_active  | BooleanField  | default=True                                                                         | Активность      |
| name       | CharField     | max_length=255, unique=True                                                          | Название группы |
| main_city  | OneToOneField | City, on_delete=models.SET_NULL, related_name="main_in_group", null=True, blank=True | Главный город   |

**Methods**

| Method  | Description                         |
| ------- | ----------------------------------- |
| __str__ | Returns the name of the city group. |

**Meta Options**

| Option              | Value                 |
| ------------------- | --------------------- |
| verbose_name        | Группа городов        |
| verbose_name_plural | Группы городов        |
| indexes             | ["name", "main_city"] |

## CustomUser

| Field           | Type          | Options                                                                                  | Description           |
| --------------- | ------------- | ---------------------------------------------------------------------------------------- | --------------------- |
| id              | AutoField     | primary_key=True                                                                         | Primary Key           |
| created_at      | DateTimeField | auto_now_add=True                                                                        | Created At            |
| updated_at      | DateTimeField | auto_now=True                                                                            | Updated At            |
| is_active       | BooleanField  | default=True                                                                             | Активность            |
| first_name      | CharField     | max_length=35, blank=True, null=True                                                     | Имя                   |
| last_name       | CharField     | max_length=35, blank=True, null=True                                                     | Фамилия               |
| email           | EmailField    | blank=True, null=True                                                                    | Почта                 |
| phone           | CharField     | max_length=16, unique=True, blank=True, null=True, help_text=_("In format +7xxxxxxxxxx") | Номер телефона        |
| address         | CharField     | max_length=1024, blank=True, null=True                                                   | Адрес                 |
| is_customer     | BooleanField  | default=False                                                                            | Покупатель ли юзер?   |
| email_confirmed | BooleanField  | default=False                                                                            | Подтверждена ли почта |
| middle_name     | CharField     | max_length=35, blank=True, null=True                                                     | Отчество              |

**Methods**

| Method  | Description                                         |
| ------- | --------------------------------------------------- |
| __str__ | Returns a formatted string with phone.              |
| delete  | Soft delete the user by setting is_active to False. |

**Meta Options**

| Option              | Value                |
| ------------------- | -------------------- |
| verbose_name        | Пользователь         |
| verbose_name_plural | Пользователи         |
| indexes             | ["phone", "address"] |


# Blog App Models

# Models Documentation

## Article

| Field      | Type            | Options                                                             | Description    |
| ---------- | --------------- | ------------------------------------------------------------------- | -------------- |
| id         | AutoField       | primary_key=True                                                    | Primary Key    |
| created_at | DateTimeField   | auto_now_add=True                                                   | Created At     |
| updated_at | DateTimeField   | auto_now=True                                                       | Updated At     |
| is_active  | BooleanField    | default=True                                                        | Активность     |
| created    | DateTimeField   | auto_now_add=True, verbose_name="Дата создания"                     | Дата создания  |
| name       | CharField       | max_length=128, verbose_name="Заголовок"                            | Заголовок      |
| text       | TextField       | verbose_name="Основной текст"                                       | Основной текст |
| products   | ManyToManyField | Product, verbose_name="Товары", blank=True, related_name="articles" | Товары         |

**Methods**

| Method  | Description                      |
| ------- | -------------------------------- |
| __str__ | Returns the name of the article. |

**Meta Options**

| Option              | Value  |
| ------------------- | ------ |
| verbose_name        | Статья |
| verbose_name_plural | Статьи |

## Feedback

| Field      | Type          | Options                                              | Description          |
| ---------- | ------------- | ---------------------------------------------------- | -------------------- |
| id         | AutoField     | primary_key=True                                     | Primary Key          |
| created_at | DateTimeField | auto_now_add=True                                    | Created At           |
| updated_at | DateTimeField | auto_now=True                                        | Updated At           |
| is_active  | BooleanField  | default=True                                         | Активность           |
| name       | CharField     | max_length=128, verbose_name="Имя отправителя"       | Имя отправителя      |
| email      | EmailField    | verbose_name="Электронная почта"                     | Электронная почта    |
| message    | TextField     | max_length=2048, verbose_name="Текст обратной связи" | Текст обратной связи |

**Methods**

| Method  | Description                                     |
| ------- | ----------------------------------------------- |
| __str__ | Returns a formatted string with name and email. |

**Meta Options**

| Option              | Value          |
| ------------------- | -------------- |
| verbose_name        | Обратная связь |
| verbose_name_plural | Обратная связь |


# Bitrix App Models

# Models Documentation

## Lead

| Поле       | Тип данных    | Опции             | Описание                 |
| ---------- | ------------- | ----------------- | ------------------------ |
| id         | AutoField     | primary_key=True  | Уникальный идентификатор |
| created_at | DateTimeField | auto_now_add=True | Дата и время создания    |
| updated_at | DateTimeField | auto_now=True     | Дата и время обновления  |
| is_active  | BooleanField  | default=True      | Активность               |
| bitrix_id  | IntegerField  | unique=True       | Идентификатор Bitrix24   |
| title      | CharField     | max_length=255    | Название лида            |
| status     | CharField     | max_length=50     | Статус лида              |

**Methods**

| Метод   | Описание                                            |
| ------- | --------------------------------------------------- |
| __str__ | Возвращает форматированную строку с названием лида. |

**Meta Options**

| Опция    | Значение |
| -------- | -------- |
| abstract | True     |

