# config/urls.py
from django.contrib import admin
from django.urls import path, include # Make sure 'include' is imported
from django.conf import settings
from django.conf.urls.static import static

# --- Import the home_view from players app ---
from players.views import home_view

urlpatterns = [
    # --- Add the path for the homepage (root URL) ---
    path('', home_view, name='home'),

    # --- Keep your other paths ---
    path('admin/', admin.site.urls),
    path('players/', include('players.urls')),

    # --- Add the built-in auth URLs ---
    # This provides login, logout, password reset, etc. views and URLs
    path('accounts/', include('django.contrib.auth.urls')),

    # If you were using your 'users' app for accounts instead, you'd include that:
    # path('accounts/', include('users.urls')),
]

# Add this section ONLY if you are in DEBUG mode and using FileField/ImageField
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # You might add static files serving later too if needed for development
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)