from django.db import models
from django.urls import reverse

from account.models import City, TimeBasedModel
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError


class Category(MPTTModel, TimeBasedModel):
    name = models.CharField(
        max_length=255,
        verbose_name="Категория",
    )

    slug = models.SlugField(unique=True)

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

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("-id",)

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "shop:product_list_by_category", kwargs={"category_slug": self.slug}
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

    def __str__(self) -> str:
        return f"{self.name}"


class Product(TimeBasedModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Категория",
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
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "shop:product_detail",
            kwargs={"product_slug": self.slug, "category_slug": self.category.slug},
        )


class Review(TimeBasedModel):
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.PROTECT, verbose_name="Товар"
    )

    name = models.CharField(
        max_length=64,
        verbose_name="Имя",
    )

    rating = models.PositiveSmallIntegerField(verbose_name="Рейтинг")
    review = models.TextField(max_length=255, verbose_name="Отзыв")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return self.name


class Characteristic(TimeBasedModel):
    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"

    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, related_name="characteristics", on_delete=models.CASCADE
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

    def __str__(self):
        return f"{self.product.title} - {self.city.name}: {self.price}"


class SettingChoices(models.TextChoices):
    MAINTENANCE = "maintenance", "Тех. работы"
    CDN_ENABLED = "cdn_enabled", "Включен ли CDN"
    CDN_ADDRESS = "cdn_address", "Адрес CDN"
    MULTIDOMAINS_ENABLED = "multidomains_enabled", "Включен ли Multidomains"
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

    key = models.CharField(
        verbose_name="Ключ", choices=SettingChoices.choices, max_length=255, unique=True
    )
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
