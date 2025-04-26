# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.

# If you haven't created any custom models specifically within the 'users' app
# (in users/models.py), then you don't need to register anything else here.
# Django automatically handles the registration of the built-in User model.

# You could potentially customize the User admin here later if needed, e.g.:
# class UserAdmin(BaseUserAdmin):
#     pass # Add customizations here
# admin.site.unregister(User) # Unregister default
# admin.site.register(User, UserAdmin) # Register customized version