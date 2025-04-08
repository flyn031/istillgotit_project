# players/admin.py

from django.contrib import admin
from .models import PlayerProfile, VideoUpload, Comment

# --- PlayerProfile Admin ---
admin.site.register(PlayerProfile)


# --- VideoUpload Admin ---
# Customize the admin display for VideoUpload
class VideoUploadAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('title', 'player_profile_user', 'uploaded_at', 'allow_comments')
    # Allow editing 'allow_comments' directly in the list view
    list_editable = ('allow_comments',)
    # Add filters
    list_filter = ('uploaded_at', 'allow_comments', 'player_profile__user__username')
    # Add search bar
    search_fields = ('title', 'description')
    # Make timestamps read-only in the detail view
    readonly_fields = ('uploaded_at',)

    # Helper method to display username from related profile (for list_display)
    @admin.display(description='Player', ordering='player_profile__user__username')
    def player_profile_user(self, obj):
        # It's safer to check if player_profile exists
        return obj.player_profile.user.username if obj.player_profile and obj.player_profile.user else 'N/A'

# Register VideoUpload using the custom admin class
admin.site.register(VideoUpload, VideoUploadAdmin)


# --- Comment Admin ---
# Customize the admin display for Comment
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author_username', 'video_title', 'body_preview', 'created_at')
    list_filter = ('created_at', 'author__username', 'video__title')
    search_fields = ('body', 'author__username')
    readonly_fields = ('created_at',) # Make timestamp read-only

    # Helper methods for display
    @admin.display(description='Author', ordering='author__username')
    def author_username(self, obj):
        return obj.author.username if obj.author else 'N/A'

    @admin.display(description='Video', ordering='video__title')
    def video_title(self, obj):
        return obj.video.title if obj.video else 'N/A'

    @admin.display(description='Comment Preview')
    def body_preview(self, obj):
        return (obj.body[:50] + '...') if len(obj.body) > 50 else obj.body

# Register Comment using the custom admin class
admin.site.register(Comment, CommentAdmin)