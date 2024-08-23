# Generated by Django 4.2.11 on 2024-08-23 14:34

from django.db import migrations, models
import django.db.models.deletion
import shop.validators.item_set


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('shop', '0031_alter_itemsetelement_item_set'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemsetelement',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', validators=[shop.validators.item_set.validate_object_exists]),
        ),
        migrations.AlterField(
            model_name='itemsetelement',
            name='item_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='elements', to='shop.itemset', verbose_name='Набор элементов'),
        ),
    ]
