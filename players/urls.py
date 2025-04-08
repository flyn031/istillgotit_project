# players/urls.py

from django.urls import path
# --- Import all the views needed by URLs in this file ---
from .views import signup_view, profile_detail_view, profile_edit_view, video_upload_view

# Define the app namespace for reversing URLs (e.g., {% url 'players:signup' %})
app_name = 'players'

urlpatterns = [
    # Auth/Profile URLs
    path('signup/', signup_view, name='signup'),
    path('profile/', profile_detail_view, name='profile_detail'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),

    # --- Add URL pattern for uploading videos ---
    # Maps /players/upload/ to the video_upload_view function
    path('upload/', video_upload_view, name='video_upload'),
]