# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings          # Import settings
from django.conf.urls.static import static # Import static
from players.views import home_view        # Import home_view directly

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home page at the root URL ('')
    path('', home_view, name='home'), # Define the 'home' URL name here

    # Include your app's URLs (excluding the root home page)
    # Use a prefix like 'players/' to avoid conflicts with other potential apps or auth urls
    path('players/', include('players.urls')),

    # Include Django's built-in auth URLs (login, logout, password reset, etc.)
    # These typically expect templates in a 'registration/' directory
    # The LOGIN_URL and LOGOUT_REDIRECT_URL in settings.py will use these names ('login', etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Include other apps if necessary
    # path('users/', include('users.urls')), # If you add user-specific views later
]

# --- Development-Only Media File Serving ---
# Add this section AFTER the urlpatterns definition
if settings.DEBUG:
    # This tells Django's development server to serve media files uploaded by users
    # from the MEDIA_ROOT directory when requested via the MEDIA_URL prefix.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Note: Static files (CSS, JS) are usually served automatically by the
    # development server when DEBUG=True and 'django.contrib.staticfiles' is in INSTALLED_APPS.
    # You generally don't need the static(settings.STATIC_URL...) line here for development.

# --- Production Note ---
# In production (DEBUG=False), never rely on this method for serving media or static files.
# Your web server (Nginx, Apache) or a dedicated service (like AWS S3 + CloudFront or WhiteNoise for static)
# should be configured to handle these files efficiently and securely.