# Generated by Django 5.1.3 on 2024-12-06 02:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0007_remove_returnitem_unit_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='returntransaction',
            name='refund_amount',
        ),
    ]