# Generated by Django 5.1.3 on 2024-12-04 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_alter_product_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='current_stock',
            field=models.IntegerField(default=0),
        ),
    ]
