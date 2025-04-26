# players/urls.py
from django.urls import path
from .views import (
    signup_view,
    profile_detail_view,
    profile_edit_view,
    video_upload_view,
    add_physical_stat_view,
    add_match_record_view,
    add_performance_stat_view,
    browse_profiles_view,
    home_view, # Ensure home_view is imported if handled here
    video_detail_view # Import the new video detail view
)

app_name = 'players'

urlpatterns = [
    # Auth/Profile URLs
    path('signup/', signup_view, name='signup'),

    # Path for viewing own profile (no pk)
    path('profile/', profile_detail_view, name='profile_detail'),

    # Path for viewing specific profiles by primary key (pk)
    path('profile/<int:pk>/', profile_detail_view, name='profile_detail_pk'),

    # Edit own profile
    path('profile/edit/', profile_edit_view, name='profile_edit'),

    # Add data URLs
    path('profile/add_physical_stat/', add_physical_stat_view, name='add_physical_stat'),
    path('profile/add_match/', add_match_record_view, name='add_match_record'),
    path('match/<int:match_id>/add_performance/', add_performance_stat_view, name='add_performance_stat'),

    # Video URLs
    path('upload/', video_upload_view, name='video_upload'),
    # --- New URL for viewing a single video ---
    path('video/<int:pk>/', video_detail_view, name='video_detail'),

    # Browse URL
    path('browse/', browse_profiles_view, name='browse_profiles'),

    # Note: Ensure your project-level urls.py correctly includes these player URLs
    # and maps the root URL ('') to the appropriate view (likely players.views.home_view).
]