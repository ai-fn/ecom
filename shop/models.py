from django.db import models
from django.urls import reverse

from account.models import City, TimeBasedModel
from mptt.models import MPTTModel, TreeForeignKey


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


class Review(models.Model):
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

    class Meta:
        verbose_name = "Цена"
        verbose_name_plural = "Цены"
        unique_together = ("product", "city")

    def __str__(self):
        return f"{self.product.title} - {self.city.name}: {self.price}"
