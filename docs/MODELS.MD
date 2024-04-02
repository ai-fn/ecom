## Shop App

1. Модель Category

| Имя парамета | Описание                                                                                 | Тип данных      | Максимальное значение |
| ------------ | ---------------------------------------------------------------------------------------- | --------------- | --------------------- |
| name         | Имя                                                                                      | Строка          | 255                   |
| slug         | Слаг ЧПУ (человекопонятный)                                                              | SlugField       | 256                   |
| parent       | Родительская категория по MPTT                                                           | TreeForeignKey  |                       |
| icon         | Иконка категории для вывода в небольших местах. Хранится category_icons/                 | FileField       |                       |
| image        | Картинка категории для вывода в списке категорий или где потребуется. Хранится category/ | ImageFIeld      |                       |
| is_visible   | Доступна ли категория напрямую или видна ли                                              | BooleanField    | по умолчанию false    |
| is_popular   | Популярна ли категория                                                                   | BooleanField    | по умолчанию false    |
| order        | Ручной ввод порядка вывода категорий                                                     | BigIntegerField |                       |


2. Модель CategoryMetaData

| Имя параметра | Описание  | Тип данных | Максимальное значение |
| ------------- | --------- | ---------- | --------------------- |
| category      | Категория | ForeignKey |
| title         | Title     | CharField  | 128                   |
| description   | Описание  | CharField  | 128                   |

3. Модель Brand

| Имя параметра | Описание                | Тип данных      | Максимальное значение |
| ------------- | ----------------------- | --------------- | --------------------- |
| name          | Имя бренда              | CharField       | 128                   |
| icon          | Иконка                  | FileField       |
| slug          | Слаг ЧПУ                | SlugField       | 256                   |
| order         | Порядковый номер бренда | BigIntegerField |

4. Модель Product

| Имя параметра             | Описание                 | Тип данных      | Максимальное значение |
| ------------------------- | ------------------------ | --------------- | --------------------- |
| category                  | Каноническая категория   | ForeignKey      |
| additional_categories     | Дополнительные категории | ManyToManyField |
| brand                     | Бренд                    | ForeignKey      |
| title                     | Наименование             | CharField       | 255                   |
| description               | Описание                 | TextField       |
| image                     | Изображение              | ImageField      |
| catalog_image             | Изображение в каталоге   | ImageField      |
| search_image              | Изображение в поиске     | ImageField      |
| slug                      | Слаг ЧПУ                 | SlugField       | 256                   |
| similar_products          | Похожие продукты         | ManyToManyField |
| in_stock                  | В наличии ли товар       | BooleanField    |
| is_popular                | Популярен ли товар       | BooleanField    |
| priority                  | Приоритет показа         | IntegerField    | 1 - 1,000,000         |
| frequenly_bought_together | Часто покупают вместе с  | ManyToManyField |

5. Модель ProductFrequenlyBoughtTogether

| Имя параметра  | Описание               | Тип данных              | Максимальное значение         |
| -------------- | ---------------------- | ----------------------- | ----------------------------- |
| product_from   | Какой товар            | ForeignKey              |
| product_to     | Вместе с каким товаром | ForeignKey              |
| purchase_count | Количество покупок     | PositiveBigIntegerField | 0 - 9,223,372,036,854,775,807 |

6. Модель ProductImage

| Имя параметра | Описание    | Тип данных | Максимальное значение |
| ------------- | ----------- | ---------- | --------------------- |
| product       | Товар       | ForeignKey |
| image         | Изображение | ImageField |

7. Модель Promo

| Имя параметра | Описание                  | Тип данных      | Максимальное значение |
| ------------- | ------------------------- | --------------- | --------------------- |
| name          | Название акции            | CharField       | 64                    |
| category      | Категория                 | ForeignKey      |
| product       | Продукт                   | ForeignKey      |
| image         | Изображение               | ImageField      |
| cities        | Города, где действует     | ManyToManyField |
| is_active     | Активна ли акция          | BooleanField    |
| active_to     | До какого времени активна | DateField       |

8. Модель Review

| Имя параметра | Описание    | Тип данных                | Максимальное значение |
| ------------- | ----------- | ------------------------- | --------------------- |
| product       | Товар       | ForeignKey                |
| user          | Комментатор | ForeignKey                |
| rating        | Рейтинг     | PositiveSmallIntegerField | 0 - 5                 |
| review        | Отзыв       | TextField                 | 255                   |

9. Модель Characteristic

| Имя параметра | Описание                | Тип данных | Максимальное значение |
| ------------- | ----------------------- | ---------- | --------------------- |
| name          | Название характеристики | CharField  | 255                   |
| category      | Категория               | ForeignKey |

10. Модель CharacteristicValue

| Имя параметра  | Описание                           | Тип данных | Максимальное значение |
| -------------- | ---------------------------------- | ---------- | --------------------- |
| product        | Товар                              | ForeignKey |
| characteristic | Характеристика                     | ForeignKey |
| value          | Значение характеристики для товара | CharField  | 255                   |

11. Модель Price

| Имя параметра | Описание    | Тип данных   | Максимальное значение |
| ------------- | ----------- | ------------ | --------------------- |
| product       | Товар       | ForeignKey   |
| city          | Город       | ForeignKey   |
| price         | Цена        | DecimalField |
| old_price     | Старая цена | DecimalField |

12. Модель Setting

| Имя параметра  | Описание              | Тип данных   | Максимальное значение |
| -------------- | --------------------- | ------------ | --------------------- |
| type           | Тип                   | CharField    |
| value_string   | Строковое значение    | CharField    | 255                   |
| value_boolean  | Логическое значение   | BooleanField |
| value_number   | Числовое значение     | IntegerField |
| predefined_key | Предопределенный ключ | CharField    | 255                   |
| custom_key     | Пользовательский ключ | CharField    | 255                   |

13. Модель FooterSettings

| Имя параметра    | Описание                                   | Тип данных           | Максимальное значение |
| ---------------- | ------------------------------------------ | -------------------- | --------------------- |
| max_footer_items | Максимальное количество элементов в футере | PositiveIntegerField |

14. Модель FooterItem

| Имя параметра   | Описание         | Тип данных           | Максимальное значение |
| --------------- | ---------------- | -------------------- | --------------------- |
| footer_settings | Настройки Footer | ForeignKey           |
| order           | Порядковый номер | PositiveIntegerField |
| title           | Наименование     | CharField            | 100                   |
| link            | Ссылка           | URLField             |

15. Модель MainPageSliderImage

| Имя параметра | Описание                 | Тип данных   | Максимальное значение |
| ------------- | ------------------------ | ------------ | --------------------- |
| order         | Порядковый номер         | IntegerField | уникальный            |
| link          | Ссылка                   | URLField     |
| title         | Заголовок на изображении | CharField    | 255                   |
| descriptions  | Заголовок на изображении | CharField    | 255                   |
| button_text   | Текст кнопки             | CharField    | 100                   |
| image         | Изображение              | ImageField   |

16. Модель MainPageCategoryBarItem

| Имя параметра | Описание         | Тип данных   | Максимальное значение |
| ------------- | ---------------- | ------------ | --------------------- |
| order         | Порядковый номер | IntegerField | уникальный            |
| link          | Ссылка           | URLField     |
| text          | Текст            | CharField    | 100                   |


## Cart App

1. Модель OrderStatus
 
| Имя параметра | Описание         | Тип данных | Максимальное значение |
| ------------- | ---------------- | ---------- | --------------------- |
| name          | Название статуса | CharField  | 128                   |

2. Модель Order

| Имя параметра | Описание      | Тип данных      | Максимальное значение |
| ------------- | ------------- | --------------- | --------------------- |
| customer      | Покупатель    | ForeignKey      |                       |
| products      | Товары        | ManyToManyField |                       |
| region        | Область       | CharField       | 255                   |
| district      | Район         | CharField       | 255                   |
| city_name     | Город         | CharField       | 255                   |
| street        | Улица         | CharField       | 255                   |
| house         | Номер дома    | CharField       | 255                   |
| total         | Сумма заказа  | DecimalField    |                       |
| status        | Статус заказа | ForeignKey      |                       |


3. Модель ProductsInOrder

| Имя параметра | Описание                     | Тип данных                | Максимальное значение |
| ------------- | ---------------------------- | ------------------------- | --------------------- |
| order         | Заказ                        | ForeignKey                |                       |
| product       | Товар                        | ForeignKey                |                       |
| quantity      | Количество товара в заказе   | PositiveSmallIntegerField |                       |
| price         | Цена товара на момент заказа | DecimalField              |                       |


4. Модель CartItem
   

| Имя параметра | Описание   | Тип данных           | Максимальное значение |
| ------------- | ---------- | -------------------- | --------------------- |
| customer      | Покупатель | ForeignKey           |                       |
| product       | Товар      | ForeignKey           |                       |
| quantity      | Количество | PositiveIntegerField |                       |


## Account App

1. Модель City

| Имя параметра      | Описание               | Тип данных      | Максимальное значение |
| ------------------ | ---------------------- | --------------- | --------------------- |
| name               | Город                  | CharField       | 255                   |
| domain             | Домен                  | CharField       | 255                   |
| address            | Адрес                  | CharField       | 256                   |
| number             | Номер телефона         | BigIntegerField |                       |
| how_to_get_office  | Как добраться до офиса | CharField       | 512                   |
| schedule           | График работы          | TextField       |                       |
| nominative_case    | Именительный падеж     | CharField       | 128                   |
| genitive_case      | Родительный падеж      | CharField       | 128                   |
| dative_case        | Дательный падеж        | CharField       | 128                   |
| accusative_case    | Винительный падеж      | CharField       | 128                   |
| instrumental_case  | Творительный падеж     | CharField       | 128                   |
| prepositional_case | Предложный падеж       | CharField       | 128                   |

2. Модель CityGroup

| Имя параметра | Описание      | Тип данных             | Максимальное значение |
| ------------- | ------------- | ---------------------- | --------------------- |
| name          | Город         | CharField              | 255                   |
| main_city     | Главный город | ForeignKey (City)      |                       |
| cities        | Города        | ManyToManyField (City) |                       |


3. Модель CustomUser

| Имя параметра | Описание            | Тип данных        | Максимальное значение |
| ------------- | ------------------- | ----------------- | --------------------- |
| phone         | Номер телефона      | CharField         | 16                    |
| city          | Город               | ForeignKey (City) |                       |
| region        | Область             | CharField         | 255                   |
| district      | Район               | CharField         | 255                   |
| city_name     | Город               | CharField         | 255                   |
| street        | Улица               | CharField         | 255                   |
| house         | Номер дома          | CharField         | 255                   |
| is_customer   | Покупатель ли юзер? | BooleanField      |                       |
| middle_name   | Отчество            | CharField         | 20                    |

