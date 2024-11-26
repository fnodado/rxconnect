# Generated by Django 5.1.3 on 2024-11-25 04:01

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('username', models.CharField(blank=True, max_length=200, null=True)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('location', models.CharField(blank=True, default='Earth', max_length=200, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('profile_image', models.ImageField(blank=True, default='static/images/profiles/user-default.png', null=True, upload_to='static/images/profiles/')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('pharmacist', 'Pharmacist'), ('assistant', 'Pharmacy Assistant'), ('cashier', 'Cashier')], max_length=15)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
