# Generated by Django 4.2.8 on 2024-02-12 10:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_city_how_to_get_office_city_number_city_schedule'),
        ('shop', '0008_category_is_visible'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=64, verbose_name='Название акции')),
                ('image', models.ImageField(upload_to='promo/', verbose_name='Изображение')),
                ('acitve_to', models.DateField(verbose_name='До какого времени акция активна?')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.category')),
                ('cities', models.ManyToManyField(related_name='promos', to='account.city')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.product')),
            ],
            options={
                'verbose_name': 'Акция',
                'verbose_name_plural': 'Акции',
            },
        ),
    ]
