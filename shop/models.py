from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError

from account.models import City, CustomUser, TimeBasedModel
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel, TimeBasedModel):
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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "api:shop:product_list_by_category", kwargs={"category_slug": self.slug}
        )

    def clean(self):
        # Проверяем, является ли категория главной (не имеет родителя)
        if self.parent and self.image:
            raise ValidationError(
                "Изображение может быть добавлено только к главной категории."
            )


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


class Product(TimeBasedModel):
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
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(
        upload_to="catalog/",
        verbose_name="Изображение",
    )
    catalog_image = models.ImageField(
        upload_to="catalog/products/",
        verbose_name="Изображение в каталоге",
    )
    search_image = models.ImageField(
        upload_to="catalog/products/",
        verbose_name="Изображение в поиске",
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
    in_stock = models.BooleanField(
        default=True,
        verbose_name="В наличии ли товар"
    )
    is_popular = models.BooleanField(
        default=False, 
        verbose_name="Популярен ли товар"
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("api:products-list", args=[self.pk])


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Товар",
    )
    image = models.ImageField(
        upload_to="catalog/products/",
        verbose_name="Изображение",
    )

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"

    def __str__(self):
        return f"Image for {self.product.title}"


class Promo(TimeBasedModel):
    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"

    name = models.CharField(
        verbose_name="Название акции",
        max_length=64,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
    )
    image = models.ImageField(
        upload_to="promo/",
        verbose_name="Изображение",
    )
    cities = models.ManyToManyField(
        City,
        related_name="promos",
        null=False,
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


class Characteristic(TimeBasedModel):
    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"

    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(
        Category,
        related_name="characteristics",
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self):
        return self.name


class CharacteristicValue(TimeBasedModel):
    class Meta:
        verbose_name = "Значение характеристики для товара"
        verbose_name_plural = "Значение характеристик для товара"

    product = models.ForeignKey(
        Product, related_name="characteristic_values", on_delete=models.CASCADE
    )
    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.characteristic.name}: {self.value}"


class Price(TimeBasedModel):
    product = models.ForeignKey(
        Product, related_name="prices", on_delete=models.CASCADE
    )
    city = models.ForeignKey(City, related_name="prices", on_delete=models.CASCADE)
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
        unique_together = ("product", "city")
        indexes = [
            models.Index(
                fields=["product", "city"]
            ),  # Compound index for common queries involving both fields
        ]

    def __str__(self):
        return f"{self.product.title} - {self.city.name}: {self.price}"


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


class FooterSettings(TimeBasedModel):
    max_footer_items = models.PositiveIntegerField(default=5)

    class Meta:
        verbose_name = "Настройки Footer"
        verbose_name_plural = "Настройки Footer"

    def __str__(self):
        return f"Настройки Footer-{self.id}"


class FooterItem(TimeBasedModel):
    footer_settings = models.ForeignKey(
        FooterSettings, on_delete=models.CASCADE, related_name="footer_items"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядковый номер")
    title = models.CharField(max_length=100, verbose_name="Наименование")
    link = models.URLField(verbose_name="Ссылка", blank=True, null=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Элемент Footer"
        verbose_name_plural = "Элементы Footer"

    def __str__(self):
        return f"Элемент Footer_{self.title}-{self.id}"

    def clean(self):
        if self.footer_settings.footer_items.count() >= FooterSettings.max_footer_items:
            raise ValidationError(
                f"Exceeded the maximum number of footer items ({FooterSettings.max_footer_items})."
            )


class MainPageSliderImage(TimeBasedModel):
    order = models.IntegerField(unique=True)
    link = models.URLField(blank=True, null=True)
    image_text = models.CharField(max_length=255, blank=True, null=True)
    button_text = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(
        upload_to="main/sliders/",
        verbose_name="Изображение",
    )

    class Meta:
        ordering = ("order",)
        verbose_name = "Изображение главной страницы"
        verbose_name_plural = "Изображения главной страницы"

    def __str__(self) -> str:
        return f"MainPageSliderImage_{self.id}"


class MainPageCategoryBarItem(TimeBasedModel):

    order = models.IntegerField(unique=True)
    link = models.URLField(blank=True, null=True)
    text = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ("order",)
        verbose_name = "Категория для панели на главной странице"
        verbose_name_plural = "Категории для панели на главной странице"

    def __str__(self) -> str:
        return f"MainPageCategoryBarItem_{self.id}"
