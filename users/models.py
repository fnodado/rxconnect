import uuid

from django.db import models
from django.contrib.auth.models import User


# Define choices for role types
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('pharmacist', 'Pharmacist'),
    ('assistant', 'Pharmacy Assistant'),
    ('cashier', 'Cashier'),
]

# Create your models here.
class Profile(models.Model):
    # Link Profile to Django's built-in User model (one-to-one relationship)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=200, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True, default="Earth")
    email = models.EmailField(unique=True, blank=True, null=True)
    profile_image = models.ImageField(null=True, blank=True, upload_to='static/images/profiles/',
                                      default="static/images/profiles/user-default.png")
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    role = models.CharField(max_length=15, default="pharmacist")

    def __str__(self):
        return str(self.user.username)

    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url