# Generated by Django 4.2.11 on 2024-08-20 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0025_alter_page_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='description',
            field=models.TextField(help_text="Шаблон описания с подстановкой названия объекта и названия города в разных падежах ()'Купить Строительные материалы в {cg_nomn} по цене {price}'\nВозможные переменные: c_nomn, c_gent, c_datv, c_accs, c_ablt, c_loct, cg_nomn, cg_gent, cg_datv, cg_accs, cg_ablt, cg_loct.(Переменные в формате [c - город / cg - группа городов]_[название падежа, начиная с именитольного])", max_length=2048, verbose_name='Описание'),
        ),
    ]