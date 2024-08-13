# Generated by Django 4.2.11 on 2024-08-12 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0019_alter_productgroup_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opengraphmeta',
            name='description',
            field=models.TextField(help_text="Шаблон описания с подстановкой названия объекта и названия города в разных падежах ()'Купить {object_name} в {city_group} по цене {price}'\nВозможные переменные: object_name, city_group, price, count, nominative_case, genitive_case, dative_case, accusative_case, instrumental_case, prepositional_case.(Наименование объекта, название области, цена, кол-во товаров в категории ...название города в падежах, начиная с именитольного)", max_length=4096, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='opengraphmeta',
            name='keywords',
            field=models.TextField(blank=True, help_text="Ключевые слова: 'купить в {prepositional_case} по цене {price}, сайдинг в {city_group}, {object_name} в городе {nominative_case}'. nВозможные переменные: object_name, city_group, price, count, nominative_case, genitive_case, dative_case, accusative_case, instrumental_case, prepositional_case. (Наименование объекта, название области, цена, кол-во товаров в категории ...название города в падежах, начиная с именитольного)", max_length=4096, null=True, verbose_name='Ключевые слова'),
        ),
        migrations.AlterField(
            model_name='opengraphmeta',
            name='title',
            field=models.CharField(help_text="Шаблон заголовка объекта с подстановкой названия города в разных падежах: 'Купить {object_name} в {prepositional_case} по цене {price}'\nВозможные переменные: object_name, city_group, price, count, nominative_case, genitive_case, dative_case, accusative_case, instrumental_case, prepositional_case. (Наименование объекта, название области, цена, кол-во товаров в категории ...название города в падежах, начиная с именитольного)", max_length=1024, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='price',
            name='old_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Старая цена (для скидки)'),
        ),
    ]