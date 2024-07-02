import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from account.models import City, CityGroup, CustomUser, TimeBasedModel
from mptt.models import MPTTModel, TreeForeignKey


class ThumbModel(TimeBasedModel):
    class Meta:
        abstract = True

    thumb_img = models.TextField(
        verbose_name="Миниатюра", null=True, blank=True, max_length=1024
    )

class Category(ThumbModel, MPTTModel):
    name = models.CharField(
        max_length=255,
        verbose_name="Категория",
    )

    slug = models.SlugField(unique=True, max_length=256)

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
        verbose_name="Порядковый номер категории", blank=True
    )
    opengraph_metadata = GenericRelation("OpenGraphMeta", related_query_name="category")

    def get_absolute_url(self):
        return f"katalog/{self.slug}"

    def __str__(self):
        return self.name

    def clean(self):
        # Проверяем, является ли категория главной (не имеет родителя)
        if self.parent and self.image:
            raise ValidationError(
                "Изображение может быть добавлено только к главной категории."
            )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("-id",)
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["parent"]),
        ]

    class MPTTMeta:
        order_insertion_by = ["name"]


class CategoryMetaData(TimeBasedModel):
    class Meta:
        verbose_name = "Метаданные категории"
        verbose_name_plural = "Метаданные категорий"

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="category_meta",
    )
    title = models.CharField(
        verbose_name="Title",
        max_length=128,
        null=True,
    )
    description = models.CharField(
        verbose_name="Описание",
        max_length=128,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.category.name} метаданные"


class Brand(TimeBasedModel):
    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        indexes = [
            models.Index(fields=["name"]),
        ]

    name = models.CharField(
        verbose_name="Имя бренда",
        default="Нет имени",
        max_length=128,
    )
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
        max_length=255
    )
    search_image = models.ImageField(
        upload_to="catalog/products/images/",
        verbose_name="Изображение в поиске",
        blank=True,
        null=True,
        max_length=255
    )
    original_image = models.ImageField(
        upload_to="catalog/products/images/",
        verbose_name="Исходное изображение",
        blank=True,
        null=True,
        max_length=255
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

    def __str__(self):
        return f"Избранный товар({self.user.username} - {self.product.title})"


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


class Promo(ThumbModel):
    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"

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
    is_active = models.BooleanField(verbose_name="Активна ли акция", default=False)
    active_to = models.DateField(verbose_name="До какого времени акция активна?")

    def __str__(self):
        return f"{self.name}"


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
    review = models.TextField(max_length=255, verbose_name="Отзыв")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["rating"]),
        ]

    def __str__(self):
        return f"Комментарий {self.user.last_name} {self.user.first_name}"






class Price(TimeBasedModel):
    product = models.ForeignKey(
        Product, related_name="prices", on_delete=models.CASCADE, verbose_name=_("Продукт")
    )
    city_group = models.ForeignKey(
        CityGroup,
        related_name="prices",
        on_delete=models.CASCADE,
        verbose_name="Группа городов",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Старая цена (для скидки)",
        null=True,
    )

    class Meta:
        verbose_name = "Цена"
        verbose_name_plural = "Цены"
        unique_together = ("product", "city_group")
        indexes = [
            models.Index(
                fields=["product", "city_group"]
            ),  # Compound index for common queries involving both fields
        ]

    def __str__(self):
        return f"{self.product.title} - {self.city_group.name}: {self.price}"


class SettingChoices(models.TextChoices):
    MAINTENANCE = "maintenance", "Тех. работы"
    CDN_ENABLED = "cdn_enabled", "Включен ли CDN"
    CDN_ADDRESS = "cdn_address", "Адрес CDN"
    MULTIDOMAINS_ENABLED = "multidomains_enabled", "Включен ли Multidomains"
    ROBOTS_TXT = "robots_txt", "Наполнение для robots.txt"
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
    order = models.PositiveIntegerField(default=0, verbose_name="Порядковый номер")
    title = models.CharField(max_length=100, verbose_name="Наименование")
    link = models.CharField(verbose_name="Ссылка", blank=False, null=False, default="#")

    class Meta:
        ordering = ["order"]
        verbose_name = "Элемент Footer"
        verbose_name_plural = "Элементы Footer"
        unique_together = ("column", "order")

    def __str__(self):
        return f"Элемент Footer_{self.title}-{self.id}"


class MainPageSliderImage(ThumbModel):
    order = models.IntegerField(unique=True, verbose_name="Порядковый номер")
    link = models.URLField(blank=True, null=True, verbose_name="Ссылка")
    title = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Заголовок"
    )
    description = models.TextField(
        max_length=1024, blank=True, null=True, verbose_name="Описание"
    )
    button_text = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Текст на кнопке"
    )
    image = models.ImageField(
        upload_to="main/sliders/",
        verbose_name="Изображение",
    )
    tiny_image = models.ImageField(
        upload_to="main/sliders/tiny",
        verbose_name="Маленькое изображение",
        null=True,
    )

    class Meta:
        ordering = ("order",)
        verbose_name = "Изображение главной страницы"
        verbose_name_plural = "Изображения главной страницы"

    def __str__(self) -> str:
        return f"MainPageSliderImage_{self.id}"


class MainPageCategoryBarItem(TimeBasedModel):

    order = models.IntegerField(verbose_name=_("Порядковый номер"), unique=True)
    link = models.CharField(verbose_name=_("Ссылка"), max_length=128)
    text = models.CharField(verbose_name=_("Текст"), max_length=100)

    class Meta:
        ordering = ("order",)
        verbose_name = "Категория для панели на главной странице"
        verbose_name_plural = "Категории для панели на главной странице"

    def __str__(self) -> str:
        return f"MainPageCategoryBarItem_{self.id}"


class SideBarMenuItem(TimeBasedModel):

    order = models.PositiveSmallIntegerField(
        default=0, verbose_name="Порядковый номер", unique=True
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
        ordering = ("order",)
        verbose_name = "Элемент бокового меню"
        verbose_name_plural = "Элементы бокового меню"

    def __str__(self) -> str:
        return f"SideBarMenuItem_{self.id}"


class ProductGroup(TimeBasedModel):

    name = models.CharField(verbose_name="Наименование", max_length=255, unique=True)
    products = models.ManyToManyField(Product, verbose_name="Продукты", blank=True)
    characteristic = models.ForeignKey(
        Characteristic,
        verbose_name="Характеристика",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Грпппа продуктов"
        verbose_name_plural = "Грпппы продуктов"

    def __str__(self):
        return f"Группа продуктов {self.name}"


class OpenGraphMeta(TimeBasedModel):

    title = models.CharField(
        verbose_name=_("Заголовок"),
        max_length=255,
    )
    description = models.TextField(
        verbose_name=_("Описание"),
        max_length=1024,
    )
    url = models.CharField(
        verbose_name=_("Ссылка"),
        max_length=255,
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


class ImageMetaData(TimeBasedModel):

    image = models.ImageField(verbose_name=_("Изображение"), upload_to="pages/")
    width = models.PositiveSmallIntegerField(
        verbose_name=_("Ширина"),
    )
    height = models.PositiveSmallIntegerField(
        verbose_name=_("Высота"),
    )
    open_graph_meta = models.ForeignKey(
        OpenGraphMeta, on_delete=models.CASCADE, verbose_name=_("Метаданные")
    )

    def __str__(self) -> str:
        return f"Изображение метаданных {self.id}"

    class Meta:
        verbose_name = _("Изображение метаданных")
        verbose_name_plural = _("Изображения метаданных")


class Page(TimeBasedModel):
    title = models.CharField(max_length=255, verbose_name=_("Наименование"))
    description = models.TextField(max_length=1024, verbose_name=_("Описание"))
    slug = models.SlugField(unique=True, verbose_name=_("Слаг страницы"))
    image = models.ImageField(
        _("Изображение"), upload_to="pages/", blank=True, null=True
    )

    opengraph_metadata = GenericRelation(OpenGraphMeta, related_query_name="page")

    class Meta:
        verbose_name = _("Страница")
        verbose_name_plural = _("Страницы")

    def __str__(self) -> str:
        return f"Страница {self.title}"

    def get_absolute_url(self):
        return f"{self.slug}"
    

class SearchHistory(TimeBasedModel):

    title = models.CharField(verbose_name=_("Заголовок поиска"), max_length=128)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_("Пользователь"))

    class Meta:
        verbose_name = _("История поиска")
        verbose_name_plural = _("Истории поиска")
        ordering = ("-created_at", )
        unique_together = (("title", "user"),)
