# Generated by Django 4.2.11 on 2024-08-26 06:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_alter_customuser_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='city',
            name='accusative_case',
        ),
        migrations.RemoveField(
            model_name='city',
            name='dative_case',
        ),
        migrations.RemoveField(
            model_name='city',
            name='genitive_case',
        ),
        migrations.RemoveField(
            model_name='city',
            name='instrumental_case',
        ),
        migrations.RemoveField(
            model_name='city',
            name='nominative_case',
        ),
        migrations.RemoveField(
            model_name='city',
            name='prepositional_case',
        ),
    ]
