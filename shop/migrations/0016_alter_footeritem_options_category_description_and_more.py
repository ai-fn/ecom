# Generated by Django 4.2.11 on 2024-08-02 06:58

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0015_alter_opengraphmeta_description_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='footeritem',
            options={'ordering': ('order',), 'verbose_name': 'Элемент Footer', 'verbose_name_plural': 'Элементы Footer'},
        ),
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, max_length=4096, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='order',
            field=models.BigIntegerField(blank=True, unique=True, verbose_name='Порядковый номер бренда'),
        ),
        migrations.AlterField(
            model_name='category',
            name='order',
            field=models.BigIntegerField(blank=True, null=True, unique=True, verbose_name='Порядковый номер категории'),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=256, unique=True, verbose_name='Слаг'),
        ),
        migrations.AlterField(
            model_name='footeritem',
            name='order',
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name='Порядковый номер'),
        ),
        migrations.AlterField(
            model_name='mainpagecategorybaritem',
            name='order',
            field=models.IntegerField(blank=True, unique=True, verbose_name='Порядковый номер'),
        ),
        migrations.AlterField(
            model_name='mainpagesliderimage',
            name='order',
            field=models.IntegerField(blank=True, unique=True, verbose_name='Порядковый номер'),
        ),
        migrations.AlterField(
            model_name='sidebarmenuitem',
            name='order',
            field=models.PositiveSmallIntegerField(blank=True, unique=True, verbose_name='Порядковый номер'),
        ),
    ]
