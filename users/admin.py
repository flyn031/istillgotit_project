# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # You can customize the admin interface for your user model here later
    # For example, add custom fields to list_display or fieldsets
    # list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_of_birth') # Example
    # fieldsets = UserAdmin.fieldsets + (
    #     ('Custom Info', {'fields': ('date_of_birth',)}), # Example
    # )
    pass

admin.site.register(CustomUser, CustomUserAdmin)