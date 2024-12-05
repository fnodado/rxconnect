# Generated by Django 5.1.3 on 2024-12-05 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_alter_purchasetransaction_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='saletransaction',
            name='status',
            field=models.CharField(choices=[('in_progress', 'In Progress'), ('completed', 'Completed')], default='in_progress', max_length=20),
        ),
    ]