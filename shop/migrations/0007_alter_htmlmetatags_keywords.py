# Generated by Django 4.2.11 on 2024-07-09 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_delete_categorymetadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='htmlmetatags',
            name='keywords',
            field=models.TextField(help_text="Ключевые слова: 'купить в {prepositional_case}, сайдинг в {city_group}, {object_name} в городе {nominative_case}'. nВозможные переменные: object_name, city_group, nominative_case, genitive_case, dative_case, accusative_case, instrumental_case, prepositional_case. (Наименование объекта, название области, ...название города в падежах, начиная с именитольного)", max_length=4096, verbose_name='Ключевые слова'),
        ),
    ]
