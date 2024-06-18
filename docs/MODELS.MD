# Shop App Models

## 1. Модель `Category`

| Имя параметра      | Описание                                                                                 | Тип данных      | Максимальное значение |
| ------------------ | ---------------------------------------------------------------------------------------- | --------------- | --------------------- |
| id                 | Идентификатор                                                                            | AutoField       | -                     |
| created_at         | Время создания                                                                           | DateTimeField   | -                     |
| updated_at         | Время обновления                                                                         | DateTimeField   | -                     |
| name               | Категория                                                                                | CharField       | 255                   |
| slug               | Слаг ЧПУ (человекопонятный)                                                              | SlugField       | 256                   |
| parent             | Родительская категория по MPTT                                                           | TreeForeignKey  | -                     |
| icon               | Иконка категории для вывода в небольших местах. Хранится category_icons/                 | FileField       | -                     |
| image              | Картинка категории для вывода в списке категорий или где потребуется. Хранится category/ | ImageField      | -                     |
| is_visible         | Доступна ли категория напрямую или видна ли                                              | BooleanField    | по умолчанию true     |
| is_popular         | Популярна ли категория                                                                   | BooleanField    | по умолчанию false    |
| order              | Ручной ввод порядка вывода категорий                                                     | BigIntegerField | -                     |
| thumb_img          | Миниатюра                                                                                | TextField       | 1024                  |
| opengraph_metadata | Метаданные OpenGraph                                                                     | GenericRelation | -                     |

## 2. Модель `CategoryMetaData`

| Имя параметра | Описание         | Тип данных    | Максимальное значение |
| ------------- | ---------------- | ------------- | --------------------- |
| id            | Идентификатор    | AutoField     | -                     |
| created_at    | Время создания   | DateTimeField | -                     |
| updated_at    | Время обновления | DateTimeField | -                     |
| category      | Категория        | ForeignKey    | -                     |
| title         | Title            | CharField     | 128                   |
| description   | Описание         | CharField     | 128                   |

## 3. Модель `Brand`

| Имя параметра | Описание                | Тип данных      | Максимальное значение |
| ------------- | ----------------------- | --------------- | --------------------- |
| id            | Идентификатор           | AutoField       | -                     |
| created_at    | Время создания          | DateTimeField   | -                     |
| updated_at    | Время обновления        | DateTimeField   | -                     |
| name          | Имя бренда              | CharField       | 128                   |
| icon          | Иконка                  | FileField       | -                     |
| slug          | Слаг ЧПУ                | SlugField       | 256                   |
| order         | Порядковый номер бренда | BigIntegerField | -                     |

## 4. Модель `Product`

| Имя параметра             | Описание                 | Тип данных      | Максимальное значение |
| ------------------------- | ------------------------ | --------------- | --------------------- |
| id                        | Идентификатор            | AutoField       | -                     |
| created_at                | Время создания           | DateTimeField   | -                     |
| updated_at                | Время обновления         | DateTimeField   | -                     |
| category                  | Каноническая категория   | ForeignKey      | -                     |
| additional_categories     | Дополнительные категории | ManyToManyField | -                     |
| brand                     | Бренд                    | ForeignKey      | -                     |
| title                     | Наименование             | CharField       | 255                   |
| description               | Описание                 | TextField       | -                     |
| catalog_image             | Изображение в каталоге   | ImageField      | 255                   |
| search_image              | Изображение в поиске     | ImageField      | 255                   |
| original_image            | Исходное изображение     | ImageField      | 255                   |
| slug                      | Слаг ЧПУ                 | SlugField       | 256                   |
| similar_products          | Похожие продукты         | ManyToManyField | -                     |
| in_stock                  | В наличии ли товар       | BooleanField    | -                     |
| is_popular                | Популярен ли товар       | BooleanField    | -                     |
| is_new                    | Новый ли товар           | BooleanField    | -                     |
| priority                  | Приоритет показа         | IntegerField    | 1 - 1,000,000         |
| frequenly_bought_together | Часто покупают вместе с  | ManyToManyField | -                     |
| article                   | Артикул                  | CharField       | 128, уникальный       |
| opengraph_metadata        | Метаданные OpenGraph     | GenericRelation | -                     |

## 5. Модель `FavoriteProduct`

| Имя параметра | Описание         | Тип данных    | Максимальное значение |
| ------------- | ---------------- | ------------- | --------------------- |
| id            | Идентификатор    | AutoField     | -                     |
| created_at    | Время создания   | DateTimeField | -                     |
| updated_at    | Время обновления | DateTimeField | -                     |
| user          | Пользователь     | ForeignKey    | -                     |
| product       | Товар            | ForeignKey    | -                     |

## 6. Модель `ProductFile`

| Имя параметра | Описание         | Тип данных    | Максимальное значение |
| ------------- | ---------------- | ------------- | --------------------- |
| id            | Идентификатор    | AutoField     | -                     |
| created_at    | Время создания   | DateTimeField | -                     |
| updated_at    | Время обновления | DateTimeField | -                     |
| product       | Продукт          | ForeignKey    | -                     |
| name          | Наименование     | CharField     | 512                   |
| file          | Файл             | FileField     | 512                   |

## 7. Модель `ProductFrequenlyBoughtTogether`

| Имя параметра  | Описание               | Тип данных              | Максимальное значение         |
| -------------- | ---------------------- | ----------------------- | ----------------------------- |
| id             | Идентификатор          | AutoField               | -                             |
| created_at     | Время создания         | DateTimeField           | -                             |
| updated_at     | Время обновления       | DateTimeField           | -                             |
| product_from   | Какой товар            | ForeignKey              | -                             |
| product_to     | Вместе с каким товаром | ForeignKey              | -                             |
| purchase_count | Количество покупок     | PositiveBigIntegerField | 0 - 9,223,372,036,854,775,807 |

## 8. Модель `ProductImage`

| Имя параметра | Описание         | Тип данных    | Максимальное значение |
| ------------- | ---------------- | ------------- | --------------------- |
| id            | Идентификатор    | AutoField     | -                     |
| created_at    | Время создания   | DateTimeField | -                     |
| updated_at    | Время обновления | DateTimeField | -                     |
| product       | Товар            | ForeignKey    | -                     |
| name          | Название         | CharField     | 255                   |
| image         | Изображение      | ImageField    | 255                   |
| thumb_img     | Миниатюра        | TextField     | 1024                  |

## 9. Модель `Promo`

| Имя параметра | Описание                         | Тип данных      | Максимальное значение |
| ------------- | -------------------------------- | --------------- | --------------------- |
| id            | Идентификатор                    | AutoField       | -                     |
| created_at    | Время создания                   | DateTimeField   | -                     |
| updated_at    | Время обновления                 | DateTimeField   | -                     |
| name          | Название акции                   | CharField       | До 64 символов        |
| categories    | Категории в акции                | ManyToManyField | -                     |
| products      | Товары в акции                   | ManyToManyField | -                     |
| image         | Изображение                      | ImageField      | -                     |
| cities        | Города                           | ManyToManyField | -                     |
| is_active     | Активна ли акция                 | BooleanField    | True/False            |
| active_to     | До какого времени акция активна? | DateField       | -                     |

## 10. Модель `Review`

| Имя параметра | Описание         | Тип данных           | Максимальное значение |
| ------------- | ---------------- | -------------------- | --------------------- |
| id            | Идентификатор    | AutoField            | -                     |
| created_at    | Время создания   | DateTimeField        | -                     |
| updated_at    | Время обновления | DateTimeField        | -                     |
| product       | Товар            | ForeignKey           | -                     |
| user          | Комментатор      | ForeignKey           | -                     |
| rating        | Рейтинг          | PositiveSmallInteger | 0 - 5                 |
| review        | Отзыв            | TextField            | До 255 символов       |

## 11. Модель `Characteristic`

| Имя

 | параметра     | Описание         | Тип данных    | Максимальное значение |
 | ------------- | ---------------- | ------------- | --------------------- |
 | id            | Идентификатор    | AutoField     | -                     |
 | created_at    | Время создания   | DateTimeField | -                     |
 | updated_at    | Время обновления | DateTimeField | -                     |
 | name          | Наименование     | CharField     | До 255 символов       |
 | slug          | Слаг             | SlugField     | До 256 символов       |
 | category      | Категория        | ForeignKey    | -                     |
 | for_filtering | Для фильтрации   | BooleanField  | -                     |

## 12. Модель `CharacteristicValue`

| Имя параметра  | Описание         | Тип данных    | Максимальное значение |
| -------------- | ---------------- | ------------- | --------------------- |
| id             | Идентификатор    | AutoField     | -                     |
| created_at     | Время создания   | DateTimeField | -                     |
| updated_at     | Время обновления | DateTimeField | -                     |
| product        | Продукт          | ForeignKey    | -                     |
| characteristic | Характеристика   | ForeignKey    | -                     |
| value          | Значение         | CharField     | До 1024 символов      |
| slug           | Слаг             | SlugField     | До 1024 символов      |

## 13. Модель `Price`

| Имя параметра | Описание         | Тип данных    | Максимальное значение |
| ------------- | ---------------- | ------------- | --------------------- |
| id            | Идентификатор    | AutoField     | -                     |
| created_at    | Время создания   | DateTimeField | -                     |
| updated_at    | Время обновления | DateTimeField | -                     |
| product       | Продукт          | ForeignKey    | -                     |
| city_group    | Группа городов   | ForeignKey    | -                     |
| price         | Цена             | DecimalField  | 10, 2                 |
| old_price     | Старая цена      | DecimalField  | 10, 2                 |

## 14. Модель `Setting`

| Имя параметра  | Описание              | Тип данных    | Максимальное значение       |
| -------------- | --------------------- | ------------- | --------------------------- |
| id             | Идентификатор         | AutoField     | -                           |
| created_at     | Время создания        | DateTimeField | -                           |
| updated_at     | Время обновления      | DateTimeField | -                           |
| type           | Тип                   | CharField     | До 50 символов              |
| value_string   | Строковое значение    | CharField     | До 255 символов             |
| value_boolean  | Логическое значение   | BooleanField  | True/False                  |
| value_number   | Числовое значение     | IntegerField  | -                           |
| predefined_key | Предопределенный ключ | CharField     | До 255 символов             |
| custom_key     | Пользовательский ключ | CharField     | До 255 символов, уникальное |

## 15. Модель `FooterItem`

| Имя параметра | Описание         | Тип данных           | Максимальное значение |
| ------------- | ---------------- | -------------------- | --------------------- |
| id            | Идентификатор    | AutoField            | -                     |
| created_at    | Время создания   | DateTimeField        | -                     |
| updated_at    | Время обновления | DateTimeField        | -                     |
| column        | Номер колонки    | PositiveSmallInteger | -                     |
| order         | Порядковый номер | PositiveIntegerField | -                     |
| title         | Наименование     | CharField            | До 100 символов       |
| link          | Ссылка           | CharField            | -                     |

## 16. Модель `MainPageSliderImage`

| Имя параметра | Описание         | Тип данных    | Максимальное значение |
| ------------- | ---------------- | ------------- | --------------------- |
| id            | Идентификатор    | AutoField     | -                     |
| created_at    | Время создания   | DateTimeField | -                     |
| updated_at    | Время обновления | DateTimeField | -                     |
| order         | Порядковый номер | IntegerField  | -                     |
| link          | Ссылка           | URLField      | -                     |
| title         | Заголовок        | CharField     | До 255 символов       |
| description   | Описание         | CharField     | До 255 символов       |
| button_text   | Текст на кнопке  | CharField     | До 100 символов       |
| image         | Изображение      | ImageField    | -                     |

## 17. Модель `MainPageCategoryBarItem`

| Имя параметра | Описание         | Тип данных    | Максимальное значение |
| ------------- | ---------------- | ------------- | --------------------- |
| id            | Идентификатор    | AutoField     | -                     |
| created_at    | Время создания   | DateTimeField | -                     |
| updated_at    | Время обновления | DateTimeField | -                     |
| order         | Порядковый номер | IntegerField  | -                     |
| link          | Ссылка           | URLField      | -                     |
| text          | Текст            | CharField     | До 100 символов       |

## 18. Модель `SideBarMenuItem`

| Имя параметра | Описание         | Тип данных           | Максимальное значение |
| ------------- | ---------------- | -------------------- | --------------------- |
| id            | Идентификатор    | AutoField            | -                     |
| created_at    | Время создания   | DateTimeField        | -                     |
| updated_at    | Время обновления | DateTimeField        | -                     |
| order         | Порядковый номер | PositiveSmallInteger | Уникальное            |
| title         | Заголовок        | CharField            | До 100 символов       |
| link          | Ссылка           | CharField            | До 255 символов       |
| icon          | Иконка           | ImageField           | -                     |

## 19. Модель `ProductGroup`

| Имя параметра  | Описание         | Тип данных      | Максимальное значение       |
| -------------- | ---------------- | --------------- | --------------------------- |
| id             | Идентификатор    | AutoField       | -                           |
| created_at     | Время создания   | DateTimeField   | -                           |
| updated_at     | Время обновления | DateTimeField   | -                           |
| name           | Наименование     | CharField       | До 255 символов, уникальное |
| products       | Продукты         | ManyToManyField | -                           |
| characteristic | Характеристика   | ForeignKey      | -                           |

## 20. Модель `OpenGraphMeta`

| Имя параметра | Описание           | Тип данных           | Максимальное значение                       |
| ------------- | ------------------ | -------------------- | ------------------------------------------- |
| id            | Идентификатор      | AutoField            | -                                           |
| created_at    | Время создания     | DateTimeField        | -                                           |
| updated_at    | Время обновления   | DateTimeField        | -                                           |
| title         | Заголовок          | CharField            | До 255 символов                             |
| description   | Описание           | TextField            | До 1024 символов                            |
| url           | Ссылка             | CharField            | До 255 символов                             |
| site_name     | Наименование сайта | CharField            | До 255 символов, по умолчанию "Кров маркет" |
| locale        | Языковой код       | CharField            | До 10 символов, формат "ru_RU"              |
| content_type  | Тип объекта        | ForeignKey           | -                                           |
| object_id     | ID объекта         | PositiveIntegerField | -                                           |

## 21. Модель `ImageMetaData`

| Имя параметра   | Описание         | Тип данных                | Максимальное значение |
| --------------- | ---------------- | ------------------------- | --------------------- |
| id              | Идентификатор    | AutoField                 | -                     |
| created_at      | Время создания   | DateTimeField             | -                     |
| updated_at      | Время обновления | DateTimeField             | -                     |
| image           | Изображение      | ImageField                | -                     |
| width           | Ширина           | PositiveSmallIntegerField | -                     |
| height          | Высота           | PositiveSmallIntegerField | -                     |
| open_graph_meta | Метаданные       | ForeignKey                | -                     |

## 22. Модель `Page`

| Имя параметра | Описание         | Тип данных    | Максимальное значение |
| ------------- | ---------------- | ------------- | --------------------- |
| id            | Идентификатор    | AutoField     | -                     |
| created_at    | Время создания   | DateTimeField | -                     |
| updated_at    | Время обновления | DateTimeField | -                     |
| title         | Наименование     | CharField     | До 255 символов       |
| description   | Описание         | TextField     | До 1024 символов      |
| slug          | Слаг страницы    | SlugField     | Уникальное            |

            |
| image         | Изображение   | ImageField | -                     |

## 23. Модель `SearchHistory`

| Имя параметра | Описание         | Тип данных    | Максимальное значение |
| ------------- | ---------------- | ------------- | --------------------- |
| id            | Идентификатор    | AutoField     | -                     |
| created_at    | Время создания   | DateTimeField | -                     |
| updated_at    | Время обновления | DateTimeField | -                     |
| title         | Заголовок поиска | CharField     | До 128 символов       |
| user          | Пользователь     | ForeignKey    | -                     |
```

# Cart App Models

## 1. Модель `OrderStatus`

| Имя параметра | Описание         | Тип данных    | Максимальное значение |
| ------------- | ---------------- | ------------- | --------------------- |
| id            | Идентификатор    | AutoField     | -                     |
| created_at    | Время создания   | DateTimeField | -                     |
| updated_at    | Время обновления | DateTimeField | -                     |
| name          | Название статуса | CharField     | До 128 символов       |

## 2. Модель `Order`

| Имя параметра | Описание         | Тип данных      | Максимальное значение |
| ------------- | ---------------- | --------------- | --------------------- |
| id            | Идентификатор    | AutoField       | -                     |
| created_at    | Время создания   | DateTimeField   | -                     |
| updated_at    | Время обновления | DateTimeField   | -                     |
| customer      | Покупатель       | ForeignKey      | -                     |
| products      | Товары           | ManyToManyField | -                     |
| total         | Сумма заказа     | DecimalField    | 10, 2                 |
| address       | Адрес            | CharField       | До 1024 символов      |
| status        | Статус заказа    | ForeignKey      | -                     |

## 3. Модель `ProductsInOrder`

| Имя параметра | Описание                     | Тип данных                | Максимальное значение |
| ------------- | ---------------------------- | ------------------------- | --------------------- |
| id            | Идентификатор                | AutoField                 | -                     |
| created_at    | Время создания               | DateTimeField             | -                     |
| updated_at    | Время обновления             | DateTimeField             | -                     |
| order         | Заказ                        | ForeignKey                | -                     |
| product       | Товар                        | ForeignKey                | -                     |
| quantity      | Количество товара в заказе   | PositiveSmallIntegerField | -                     |
| price         | Цена товара на момент заказа | DecimalField              | 10, 2                 |

## 4. Модель `CartItem`

| Имя параметра | Описание         | Тип данных      | Максимальное значение |
| ------------- | ---------------- | --------------- | --------------------- |
| id            | Идентификатор    | AutoField       | -                     |
| created_at    | Время создания   | DateTimeField   | -                     |
| updated_at    | Время обновления | DateTimeField   | -                     |
| customer      | Покупатель       | ForeignKey      | -                     |
| product       | Товар            | ForeignKey      | -                     |
| quantity      | Количество       | PositiveInteger | -                     |

# Account App Models

## 1. Модель `City`

| Имя параметра      | Описание               | Тип данных              | Максимальное значение      |
| ------------------ | ---------------------- | ----------------------- | -------------------------- |
| id                 | Идентификатор          | AutoField               | -                          |
| created_at         | Время создания         | DateTimeField           | -                          |
| updated_at         | Время обновления       | DateTimeField           | -                          |
| name               | Город                  | CharField               | До 255 символов, null      |
| domain             | Домен                  | CharField               | До 255 символов, null      |
| address            | Адрес                  | CharField               | До 256 символов, null      |
| number             | Номер телефона         | BigIntegerField         | По умолчанию 0             |
| how_to_get_office  | Как добраться до офиса | CharField               | До 512 символов, null      |
| schedule           | График работы          | TextField               | По умолчанию "Отсутствует" |
| nominative_case    | Именительный падеж     | CharField               | До 128 символов, null      |
| genitive_case      | Родительный падеж      | CharField               | До 128 символов, null      |
| dative_case        | Дательный падеж        | CharField               | До 128 символов, null      |
| accusative_case    | Винительный падеж      | CharField               | До 128 символов, null      |
| instrumental_case  | Творительный падеж     | CharField               | До 128 символов, null      |
| prepositional_case | Предложный падеж       | CharField               | До 128 символов, null      |
| population         | Численность населения  | PositiveBigIntegerField | По умолчанию 0             |

## 2. Модель `CityGroup`

| Имя параметра | Описание         | Тип данных      | Максимальное значение       |
| ------------- | ---------------- | --------------- | --------------------------- |
| id            | Идентификатор    | AutoField       | -                           |
| created_at    | Время создания   | DateTimeField   | -                           |
| updated_at    | Время обновления | DateTimeField   | -                           |
| name          | Название группы  | CharField       | До 255 символов, уникальное |
| main_city     | Главный город    | ForeignKey      | -                           |
| cities        | Города           | ManyToManyField | -                           |

## 3. Модель `CustomUser`

| Имя параметра   | Описание            | Тип данных    | Максимальное значение            |
| --------------- | ------------------- | ------------- | -------------------------------- |
| id              | Идентификатор       | AutoField     | -                                |
| created_at      | Время создания      | DateTimeField | -                                |
| updated_at      | Время обновления    | DateTimeField | -                                |
| first_name      | Имя                 | CharField     | До 35 символов, null             |
| last_name       | Фамилия             | CharField     | До 35 символов, null             |
| email           | Почта               | EmailField    | -                                |
| phone           | Номер телефона      | CharField     | До 16 символов, уникальное, null |
| address         | Адрес               | CharField     | До 1024 символов, null           |
| is_customer     | Покупатель          | BooleanField  | True/False                       |
| email_confirmed | Подтверждение email | BooleanField  | True/False                       |
| middle_name     | Отчество            | CharField     | До 35 символов, null             |
