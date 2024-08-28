import os

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator, validate_image_file_extension
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from unidecode import unidecode

from account.models import City, CityGroup, CustomUser, TimeBasedModel
from mptt.models import MPTTModel, TreeForeignKey

from shop.validators import validate_object_exists, FileSizeValidator


class ThumbModel(TimeBasedModel):
    class Meta:
        abstract = True

    thumb_img = models.TextField(
        verbose_name="Миниатюра", null=True, blank=True, max_length=1024
    )


class Category(MPTTModel, ThumbModel):
    name = models.CharField(
        max_length=255,
        verbose_name="Категория",
    )
    description = models.TextField(_("Описание"), max_length=4096, blank=True, null=True)
    h1_tag = models.CharField(_("h1 тэг"), max_length=512, blank=True, null=True)
    slug = models.SlugField(_("Слаг"), unique=True, max_length=256)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Каталог",
    )
    icon = models.FileField(
        upload_to="category_icons/",
        verbose_name="Иконка",
        null=True,
        blank=True,
    )
    image = models.ImageField(
        upload_to="category/",
        verbose_name="Изображение",
        null=True,
        blank=True,
    )
    is_visible = models.BooleanField(
        verbose_name="Видна ли категория (ВЕЗДЕ)",
        default=True,
    )
    is_popular = models.BooleanField(
        verbose_name="Популярна ли категория",
        default=False,
    )
    order = models.BigIntegerField(
        verbose_name="Порядковый номер категории", blank=True, null=True
    )
    opengraph_metadata = GenericRelation("OpenGraphMeta", related_query_name="category")

    def get_absolute_url(self):
        return f"katalog/{self.slug}"

    def __str__(self):
        return self.name


    def clean(self):
        if self.parent and self.image:
            raise ValidationError(
                "Изображение может быть добавлено только к главной категории."
            )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("order", "-created_at")
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["parent"]),
        ]

    class MPTTMeta:
        order_insertion_by = ["name"]
    

class Brand(TimeBasedModel):
    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        indexes = [
            models.Index(fields=["name"]),
        ]
        ordering = ("order", "name", "-created_at")

    name = models.CharField(
        verbose_name="Имя бренда",
        default="Нет имени",
        max_length=128,
    )
    h1_tag = models.CharField(_("h1 тэг"), max_length=512, blank=True, null=True)
    icon = models.FileField(
        upload_to="category_icons/",
        verbose_name="Иконка",
        null=True,
        blank=True,
    )
    slug = models.SlugField(
        unique=True,
        max_length=256,
    )
    order = models.BigIntegerField(verbose_name="Порядковый номер бренда", blank=True)

    def __str__(self) -> str:
        return f"{self.name}"


class Product(ThumbModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Каноническая категория",
    )
    additional_categories = models.ManyToManyField(
        Category,
        related_name="additional_products",
        verbose_name="Дополнительные категории",
        blank=True,
    )
    h1_tag = models.CharField(_("h1 тэг"), max_length=512, blank=True, null=True)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Бренд",
        null=True,
        blank=True,
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Наименование",
    )
    description = models.TextField(verbose_name="Описание", null=True, blank=True)
    catalog_image = models.ImageField(
        upload_to="catalog/products/images/",
        verbose_name="Изображение в каталоге",
        blank=True,
        null=True,
        max_length=255,
    )
    search_image = models.ImageField(
        upload_to="catalog/products/images/",
        verbose_name="Изображение в поиске",
        blank=True,
        null=True,
        max_length=255,
    )
    original_image = models.ImageField(
        upload_to="catalog/products/images/",
        verbose_name="Исходное изображение",
        blank=True,
        null=True,
        max_length=255,
    )
    slug = models.SlugField(
        unique=True,
        max_length=256,
    )
    similar_products = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name="Похожие продукты",
    )
    in_stock = models.BooleanField(default=True, verbose_name="В наличии ли товар")
    is_popular = models.BooleanField(default=False, verbose_name="Популярен ли товар")
    is_new = models.BooleanField(default=False, verbose_name=_("Новый ли товар"))
    priority = models.IntegerField(
        default=500,
        verbose_name="Приоритет показа",
        validators=[
            MaxValueValidator(10**6),
            MinValueValidator(1),
        ],
    )
    frequenly_bought_together = models.ManyToManyField(
        "self",
        through="ProductFrequenlyBoughtTogether",
        blank=True,
        verbose_name="Часто покупают вместе с",
    )
    article = models.CharField(
        verbose_name="Артикул",
        max_length=128,
        unique=True,
    )
    unavailable_in = models.ManyToManyField(City, related_query_name="product", verbose_name=_("Недоступен в городах"), blank=True)
    opengraph_metadata = GenericRelation("OpenGraphMeta", related_query_name="product")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["category"]),
            models.Index(fields=["article"]),
        ]
        ordering = ("-priority", "title", "-created_at")


    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = self.title
            models.Model.save(self, *args, **kwargs)
            self.slug = f"{slugify(unidecode(self.title))}-{self.id}"

        return super().save(*args, **kwargs)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return os.path.join("katalog", self.category.slug, self.slug)


class FavoriteProduct(TimeBasedModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="favorite_products",
        verbose_name=_("Пользователь"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name=_("Товар"),
    )

    class Meta:
        unique_together = ("user", "product")
        verbose_name = _("Избранный товар")
        verbose_name_plural = _("Избранные товары")
        ordering = ("user", "-created_at")

    def __str__(self):
        return f"Избранный товар({self.user.username} - {self.product.title})"


class ProductFile(TimeBasedModel):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Продукт"),
        related_name="files",
    )
    name = models.CharField(verbose_name=_("Наименование"), max_length=512)
    file = models.FileField(
        verbose_name=_("Файл"), max_length=512, upload_to="catalog/products/documents/"
    )

    class Meta:
        verbose_name = _("Документация")
        verbose_name_plural = _("Документация")
        unique_together = (("product", "name"),)
        ordering = ("product", "name", "-created_at")


class ProductFrequenlyBoughtTogether(TimeBasedModel):
    product_from = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="Какой товар",
        related_name="product_from",
    )
    product_to = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="Вместе с каким товаром",
        related_name="product_to",
    )
    purchase_count = models.PositiveBigIntegerField(
        default=0, verbose_name="Количество покупок"
    )

    class Meta:
        verbose_name = "Часто покупают вместе"
        verbose_name_plural = "Часто покупают вместе"
        unique_together = (("product_from", "product_to"),)


class ProductImage(ThumbModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Товар",
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    image = models.ImageField(
        upload_to="catalog/products/images/", verbose_name="Изображение", max_length=255
    )

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ("product", "name", "-created_at")

    def __str__(self):
        return f"Image for {self.product.title}"


class Promo(ThumbModel):
    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ("-created_at",)

    name = models.CharField(
        verbose_name="Название акции",
        max_length=64,
    )
    categories = models.ManyToManyField(
        Category, verbose_name="Категории в акции", related_name="promos", blank=True
    )
    products = models.ManyToManyField(
        Product, verbose_name="Товары в акции", related_name="promos", blank=True
    )
    image = models.ImageField(
        upload_to="promo/",
        verbose_name="Изображение",
    )
    cities = models.ManyToManyField(
        City,
        related_name="promos",
    )
    active_to = models.DateField(verbose_name="До какого времени акция активна?")

    def __str__(self):
        return f"{self.name}"


class Characteristic(TimeBasedModel):
    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"
        ordering = ("name", "-created_at")

    name = models.CharField(max_length=255, verbose_name=_("Наименование"))
    slug = models.SlugField(_("Слаг"), unique=True, max_length=256)
    categories = models.ManyToManyField(
        Category,
        related_name="characteristics",
        verbose_name=_("Категории"),
    )
    for_filtering = models.BooleanField(
        _("Для фильтрации"),
        default=False,
        help_text=_("Будет ли эта характеристика отображаться в фильтрах товаров"),
        blank=True,
    )

    def __str__(self):
        return self.name


class CharacteristicValue(TimeBasedModel):
    class Meta:
        verbose_name = "Значение характеристики для товара"
        verbose_name_plural = "Значение характеристик для товара"
        unique_together = ("characteristic", "product")
        ordering = ("-created_at",)

    product = models.ForeignKey(
        Product,
        verbose_name=_("Продукт"),
        related_name="characteristic_values",
        on_delete=models.CASCADE,
    )
    characteristic = models.ForeignKey(
        Characteristic, verbose_name=_("Характеристика"), on_delete=models.CASCADE
    )
    value = models.CharField(verbose_name=_("Значение"), max_length=1024)
    slug = models.SlugField(
        verbose_name=_("Слаг"), null=False, blank=False, max_length=1024
    )

    def save(self, *args, **kwargs) -> None:
        def is_float(value: str) -> bool:
            try:
                float(value)
                return True
            except ValueError:
                return False

        if not self.slug:
            if self.value.isdigit() or is_float(self.value):
                self.slug = self.value.replace(".", "_").replace(",", "-")
            else:
                self.slug = slugify(unidecode(str(self.value)))

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.characteristic.name}: {self.value}"


class Review(TimeBasedModel):
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.PROTECT, verbose_name="Товар"
    )
    user = models.ForeignKey(
        CustomUser,
        verbose_name="Комментатор",
        related_name="comments",
        on_delete=models.PROTECT,
    )
    rating = models.PositiveSmallIntegerField(
        verbose_name="Рейтинг", validators=[MaxValueValidator(5)]
    )
    review = models.TextField(max_length=400, verbose_name="Отзыв", blank=True, null=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["rating"]),
        ]
        ordering = ("product", "user", "-created_at")

    def __str__(self):
        return f"Комментарий {self.user.last_name} {self.user.first_name}"


class Price(TimeBasedModel):
    product = models.ForeignKey(
        Product,
        related_name="prices",
        on_delete=models.CASCADE,
        verbose_name=_("Продукт"),
    )
    city_group = models.ForeignKey(
        CityGroup,
        related_name="prices",
        on_delete=models.CASCADE,
        verbose_name="Группа городов",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена", 
        validators=[MinValueValidator(1)],
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Старая цена (для скидки)",
        null=True,
        blank=True,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Цена"
        verbose_name_plural = "Цены"
        unique_together = ("product", "city_group")
        indexes = [
            models.Index(
                fields=["product", "city_group"]
            ),
        ]
        ordering = ("product", "-created_at")

    def __str__(self):
        return f"{self.product.title} - {self.city_group.name}: {self.price}"


class SettingChoices(models.TextChoices):
    MAINTENANCE = "maintenance", "Тех. работы"
    CDN_ENABLED = "cdn_enabled", "Включен ли CDN"
    CDN_ADDRESS = "cdn_address", "Адрес CDN"
    MULTIDOMAINS_ENABLED = "multidomains_enabled", "Включен ли Multidomains"
    ROBOTS_TXT = "robots_txt", "Наполнение для robots.txt"
    OPEN_GRAPH_META_IMAGE = "openGraphMeta_image", "Путь до openGraphMeta изображения от корня директории сайта"
    # TODO добавить настройки платежных систем
    # TODO добавить доступность прямой оплаты
    # TODO добавить настройки водяного знака на изображение
    # TODO включение CMS режима


class SettingsTypeChoices(models.TextChoices):
    BOOLEAN = "boolean", "Boolean"
    STRING = "string", "Строка"
    NUMBER = "number", "Число"


class Setting(TimeBasedModel):
    class Meta:
        verbose_name = "Настройка"
        verbose_name_plural = "Настройки"
        ordering = ("-created_at", )

    type = models.CharField(
        verbose_name="Тип",
        choices=SettingsTypeChoices.choices,
        max_length=50,
        default=SettingsTypeChoices.BOOLEAN,
    )
    value_string = models.CharField(
        verbose_name="Строковое значение", max_length=255, null=True, blank=True
    )
    value_boolean = models.BooleanField(
        verbose_name="Логическое значение", null=True, blank=True
    )
    value_number = models.IntegerField(
        verbose_name="Числовое значение", null=True, blank=True
    )
    predefined_key = models.CharField(
        verbose_name="Предопределенный ключ",
        choices=SettingChoices.choices,
        max_length=255,
        null=True,
        blank=True,
    )
    custom_key = models.CharField(
        verbose_name="Пользовательский ключ",
        max_length=255,
        null=True,
        blank=True,
        unique=True,
    )

    def clean(self):
        if not self.predefined_key and not self.custom_key:
            raise ValidationError(
                "Необходимо указать либо предопределенный ключ, либо пользовательский ключ."
            )
        if self.predefined_key and self.custom_key:
            raise ValidationError(
                "Укажите только один ключ: либо предопределенный, либо пользовательский."
            )

    def get_value(self):
        if self.type == SettingsTypeChoices.BOOLEAN:
            return self.value_boolean
        elif self.type == SettingsTypeChoices.STRING:
            return self.value_string
        elif self.type == SettingsTypeChoices.NUMBER:
            return self.value_number
        return None

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_key(self):
        return self.predefined_key or self.custom_key

    def __str__(self) -> str:
        return f"{self.get_key()}: {self.get_value()}"


class FooterItem(TimeBasedModel):
    column = models.PositiveSmallIntegerField(_("Номер колонки"))
    order = models.PositiveIntegerField(default=0, verbose_name="Порядковый номер", blank=True)
    title = models.CharField(max_length=100, verbose_name="Наименование")
    link = models.CharField(verbose_name="Ссылка", blank=False, null=False, default="#")

    class Meta:
        ordering = ("column", "order", "-created_at")
        verbose_name = "Элемент Footer"
        verbose_name_plural = "Элементы Footer"
        unique_together = ("column", "order")

    def __str__(self):
        return f"Элемент Footer_{self.title}-{self.id}"


class Banner(TimeBasedModel):
    order = models.PositiveIntegerField(
        _("Порядковый номер"), default=0
    )
    link = models.URLField(_("Ссылка"), blank=True, null=True)
    title = models.CharField(
        _("Заголовок"), max_length=255, blank=True, null=True
    )
    description = models.TextField(
        _("Описание"), max_length=1024, blank=True, null=True
    )
    button_text = models.CharField(
        _("Текст на кнопке"), max_length=100, blank=True, null=True
    )
    image = models.ImageField(
        upload_to="main/banners",
        verbose_name="Изображение",
        validators=[FileSizeValidator(2), validate_image_file_extension]
    )
    tiny_image = models.ImageField(
        _("Маленькое изображение"),
        upload_to="main/banners/tiny",
        null=True,
        blank=True,
        validators=[FileSizeValidator(2), validate_image_file_extension]
    )

    class Meta:
        ordering = ("order", "-created_at")
        verbose_name = _("Баннер")
        verbose_name_plural = _("Баннеры")

    def __str__(self) -> str:
        return f"Баннер-{self.id} {self.title}"


class MainPageCategoryBarItem(TimeBasedModel):

    order = models.IntegerField(verbose_name=_("Порядковый номер"), blank=True)
    link = models.CharField(verbose_name=_("Ссылка"), max_length=128)
    text = models.CharField(verbose_name=_("Текст"), max_length=100)

    class Meta:
        ordering = ("order", "-created_at")
        verbose_name = "Категория для панели на главной странице"
        verbose_name_plural = "Категории для панели на главной странице"

    def __str__(self) -> str:
        return f"MainPageCategoryBarItem_{self.id}"


class SideBarMenuItem(TimeBasedModel):

    order = models.PositiveSmallIntegerField(
        verbose_name="Порядковый номер", blank=True
    )
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    link = models.CharField(max_length=255, verbose_name="Ссылка")
    icon = models.CharField(
        verbose_name=_("Заголовок иконки"),
        null=True,
        blank=True,
        max_length=32,
        help_text=_("delivery, documentation, cart, orders, profile, info"),
    )

    class Meta:
        ordering = ("order", "-created_at")
        verbose_name = "Элемент бокового меню"
        verbose_name_plural = "Элементы бокового меню"

    def __str__(self) -> str:
        return f"SideBarMenuItem_{self.id}"


class ProductGroup(TimeBasedModel):

    name = models.CharField(verbose_name="Наименование", max_length=255, blank=True, null=True)
    products = models.ManyToManyField(Product, verbose_name="Продукты", blank=True, related_name="groups")
    characteristic = models.ForeignKey(
        Characteristic,
        verbose_name="Характеристика",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ("name", "-created_at")
        verbose_name = "Грпппа продуктов"
        verbose_name_plural = "Грпппы продуктов"

    def __str__(self):
        return f"Группа продуктов {self.name}"


class OpenGraphMeta(TimeBasedModel):

    title = models.CharField(
        _("Заголовок"),
        max_length=1024,
        help_text="Шаблон заголовка объекта с подстановкой названия города в разных падежах:"
        " 'Купить {object_name} в {loct} по цене {price}'\nВозможные переменные: object_name, city_group, price, count, nomn, gent, datv, accs, ablt, loct."
        " (Наименование объекта, название области, цена, кол-во товаров в категории ...название города в падежах, начиная с именитольного)",
    )
    description = models.TextField(
        _("Описание"),
        max_length=4096,
        help_text="Шаблон описания с подстановкой названия объекта и названия города в разных падежах ()"
        "'Купить {object_name} в {city_group} по цене {price}'\nВозможные переменные: object_name, city_group, price, count, nomn, gent, datv, accs, ablt, loct."
        "(Наименование объекта, название области, цена, кол-во товаров в категории ...название города в падежах, начиная с именитольного)",
    )
    keywords = models.TextField(
        _("Ключевые слова"),
        max_length=4096,
        blank=True, null=True,
        help_text="Ключевые слова: 'купить в {loct} по цене {price}, сайдинг в {city_group}, {object_name} в городе {nomn}'. nВозможные переменные: object_name, city_group, price, count, nomn, gent, datv, accs, ablt, loct."
        " (Наименование объекта, название области, цена, кол-во товаров в категории ...название города в падежах, начиная с именитольного)",
    )
    url = models.CharField(
        verbose_name=_("Ссылка"),
        max_length=255,
        help_text="Ссылка на объект без указания домена пример: '/katalog/vodostochka/dummy-product-2234/'"
    )
    site_name = models.CharField(
        verbose_name=_("Наименование сайта"), max_length=255, default="Кров маркет"
    )
    locale = models.CharField(
        verbose_name=_("Языковой код"),
        help_text=_("В формате ru_Ru"),
        max_length=10,
        default="ru_RU",
        null=True,
        blank=True,
    )
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name=_("Тип объекта")
    )
    object_id = models.PositiveIntegerField(verbose_name=_("ID объекта"))
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self) -> str:
        return f"Метаданные для {self.content_object}"

    class Meta:
        verbose_name = _("Метаданные")
        verbose_name_plural = _("Метаданные")


class Page(TimeBasedModel):
    title = models.CharField(max_length=255, verbose_name=_("Наименование"))
    content = models.TextField(
        _("Контент страницы"),
        blank=True,
        null=True,
    )
    description = models.TextField(
        max_length=2048,
        verbose_name=_("Описание"),
        help_text=f"Шаблон описания с подстановкой названия объекта и названия города в разных падежах ()"
        "'Купить Строительные материалы в {cg_nomn}'\nВозможные переменные: c_nomn, c_gent, c_datv, c_accs, c_ablt, c_loct, cg_nomn, cg_gent, cg_datv, cg_accs, cg_ablt, cg_loct."
        "(Переменные в формате [c - город / cg - группа городов]_[название падежа, начиная с именитольного])"
    )
    h1_tag = models.CharField(_("h1 тэг"), max_length=512, blank=True, null=True)
    slug = models.SlugField(unique=True, verbose_name=_("Слаг страницы"))
    image = models.ImageField(
        _("Изображение"), upload_to="pages/", blank=True, null=True
    )

    opengraph_metadata = GenericRelation(OpenGraphMeta, related_query_name="page")

    class Meta:
        verbose_name = _("Страница")
        verbose_name_plural = _("Страницы")
        ordering = ("title", "-created_at")

    def __str__(self) -> str:
        return f"Страница {self.title}"

    def get_absolute_url(self):
        return f"{self.slug}"


class SearchHistory(TimeBasedModel):

    title = models.CharField(verbose_name=_("Заголовок поиска"), max_length=128)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name=_("Пользователь")
    )

    class Meta:
        verbose_name = _("История поиска")
        verbose_name_plural = _("Истории поиска")
        ordering = ("user", "title", "-created_at",)
        unique_together = (("title", "user"),)


class ItemSet(TimeBasedModel):

    class ItemSetType(models.TextChoices):
        PRODUCT = "product", _("Товар")
        BANNER = "banner", _("Баннер")
    
    class GridType(models.TextChoices):
        grid_type_1 = "grid_type_1", _("Тип таблицы 1")
        grid_type_2 = "grid_type_2", _("Тип таблицы 2")
        grid_type_3 = "grid_type_3", _("Тип таблицы 3")
        grid_type_4 = "grid_type_4", _("Тип таблицы 4")

    title = models.CharField(_("Заголовок"), max_length=256, unique=True)
    description = models.TextField(_("Описание"), max_length=1024)
    grid_type = models.CharField(_("Тип таблицы"), choices=GridType.choices, blank=True, null=True, help_text="Доступно только для объектов типа 'Баннер'")
    order = models.PositiveIntegerField(_("Порядковый номер"), default=0)
    itemset_type = models.CharField(_("Тип объектов набора"), choices=ItemSetType.choices, max_length=64, default=ItemSetType.PRODUCT)

    def clean(self):
        if self.itemset_type not in self.ItemSetType.values:
            raise ValidationError(f'Model "{self.itemset_type}" is not allowed.')
        
        if self.grid_type and self.itemset_type != "banner":
            raise ValidationError(f'"grid_type" field allowed only for "banner" items type.')
        
        if self.grid_type not in self.GridType.values:
            raise ValidationError(f"Invalid 'grid_type' value, expected one of '{self.GridType.values}'")

        return super().clean()
    
    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)


    class Meta:
        verbose_name = _("Набор объектов")
        verbose_name_plural = _("Наборы объектов")
        ordering = ("order", "-created_at")

    def __str__(self) -> str:
        return f"Набор объектов '{self.title}'"


class ItemSetElement(TimeBasedModel):

    item_set = models.ForeignKey(ItemSet, on_delete=models.CASCADE, verbose_name=_("Набор элементов"), related_name="elements")
    order = models.PositiveIntegerField(_("Порядковый номер"), default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(_("ID элемента"))
    content_object = GenericForeignKey('content_type', 'object_id')
    
    def clean(self) -> None:
        if self.content_type.model != self.item_set.itemset_type:
            raise ValidationError(f"ItemSetElement object type do not match with ItemSet type, expected '{self.item_set.itemset_type}'")

        validate_object_exists(self.content_type, self.object_id)
        return super().clean()
    
    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Элемент набора объектов")
        verbose_name_plural = _("Элементы набора объектов")
        unique_together = (("content_type", "object_id", "item_set"),)
        ordering = ("order", "-created_at")

    def __str__(self) -> str:
        return f"{self.content_object} in {self.item_set}"
