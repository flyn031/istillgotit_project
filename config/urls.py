# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from players.views import home_view
from django.contrib.auth import views as auth_views # <-- Import auth views

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('players/', include('players.urls')), # <-- Keep this included

    # --- Explicitly define auth URLs ---
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            template_name='players/login.html'
        ),
        name='login'
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(next_page='home'),
        name='logout'
    ),

    # --- Password Reset URLs (UNCOMMENTED) ---
    path('accounts/password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='players/password_reset_form.html', # You'll need to create this template
             email_template_name='players/password_reset_email.html', # You'll need to create this email template
             subject_template_name='players/password_reset_subject.txt' # You'll need to create this subject template
         ),
         name='password_reset'), # <-- UNCOMMENTED
    path('accounts/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='players/password_reset_done.html' # You'll need to create this template
         ),
         name='password_reset_done'), # <-- UNCOMMENTED
    path('accounts/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='players/password_reset_confirm.html' # You'll need to create this template
         ),
         name='password_reset_confirm'), # <-- UNCOMMENTED
    path('accounts/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='players/password_reset_complete.html' # You'll need to create this template
         ),
         name='password_reset_complete'), # <-- UNCOMMENTED

    # --- Make sure this is commented out or removed ---
    # path('accounts/', include('django.contrib.auth.urls')),
]

# --- Media Files Serving (for development) ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)