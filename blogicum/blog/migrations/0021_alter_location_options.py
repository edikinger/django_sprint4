# Generated by Django 3.2.16 on 2025-03-16 15:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0020_auto_20250316_1814'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='location',
            options={'verbose_name': 'местоположение', 'verbose_name_plural': 'Местоположения'},
        ),
    ]
