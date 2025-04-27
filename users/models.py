# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # You can add custom fields here later if needed. Examples:
    # email = models.EmailField(unique=True) # If you want email as the primary identifier
    # date_of_birth = models.DateField(null=True, blank=True) # Example field

    def __str__(self):
        return self.username # Or self.email if you customize further