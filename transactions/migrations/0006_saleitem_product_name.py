# Generated by Django 5.1.3 on 2024-12-05 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_purchasetransaction_product_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleitem',
            name='product_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
