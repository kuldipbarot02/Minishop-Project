# Generated by Django 4.2.3 on 2023-07-20 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_brand',
            field=models.CharField(choices=[('Puma', 'Puma'), ('Rebook', 'Rebook'), ('Adidas', 'Adidas'), ('Calcetto', 'Calcetto'), ('Bata', 'Bata')], max_length=100),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_category',
            field=models.CharField(choices=[('Formal', 'Formal'), ('Sports', 'Sports'), ('Casual', 'Casual')], max_length=100),
        ),
    ]
