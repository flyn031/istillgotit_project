# players/models.py

from django.db import models
from django.conf import settings # Needed to link comments/profiles to User model

# ===================
# Player Profile Model
# ===================
class PlayerProfile(models.Model):
    """
    Represents a player's profile, linked to a standard Django User account.
    """
    # Link to the built-in User model (One User has One Profile)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,       # Delete profile if user is deleted
        related_name='player_profile' # Access profile via user.player_profile
    )

    # Profile-specific fields
    bio = models.TextField(
        blank=True,                     # Field is optional in forms
        null=True,                      # Database can store NULL if empty
        help_text="A short biography of the player."
    )
    date_of_birth = models.DateField(
        "Date of Birth",                # Verbose name for labels/admin
        blank=True,                     # Optional
        null=True                       # Optional
    )
    avatar = models.ImageField(
        "Avatar",
        upload_to='avatars/', # Saved to MEDIA_ROOT/avatars/
        null=True,            # Allow profile to have no avatar
        blank=True            # Allow form submission without an avatar
    )
    # --- ADDED CONTACT EMAIL FIELD ---
    contact_email = models.EmailField(
        "Contact Email (for scouts)",
        max_length=254, # Standard max length for emails
        blank=True,     # Optional field
        null=True,      # Allow database null
        help_text="Optional: Provide an email address if you wish to be contacted by verified scouts."
    )
    # --- END ADDITION ---

    # Timestamps (Optional but good practice)
    created_at = models.DateTimeField(auto_now_add=True) # Set on creation
    updated_at = models.DateTimeField(auto_now=True)     # Set on every save

    def __str__(self):
        """
        String representation for admin and debugging.
        """
        return f"{self.user.username}'s Profile"

    # Optional: Add a method to get avatar URL, handling cases where it's missing
    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        else:
            # Provide a default avatar image URL if needed
            # return '/static/players/images/default-avatar.png' # Example path
            return None # Or return None if no default


# ===================
# Video Upload Model
# ===================
class VideoUpload(models.Model):
    """
    Represents a video uploaded by a player.
    """
    # Link back to the player's profile using a ForeignKey
    player_profile = models.ForeignKey(
        PlayerProfile,
        on_delete=models.CASCADE, # If profile is deleted, delete their videos too
        related_name='videos'     # Allows access via profile.videos.all()
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField(
        "Video File",
        upload_to='videos/', # Saved to MEDIA_ROOT/videos/
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    allow_comments = models.BooleanField(
        "Allow Comments",
        default=True,
        help_text="Check this box to allow users to comment on this video."
    )

    class Meta:
        ordering = ['-uploaded_at'] # Show newest videos first by default

    def __str__(self):
        """
        String representation for admin and debugging.
        """
        return f"'{self.title}' by {self.player_profile.user.username}"


# ===============
# Comment Model
# ===============
class Comment(models.Model):
    """
    Represents a comment on a specific video.
    """
    # Link to the video the comment is associated with
    video = models.ForeignKey(
        VideoUpload,
        on_delete=models.CASCADE,    # If video deleted, delete comments
        related_name='comments'      # Access via video.comments.all()
    )
    # Link to the user who wrote the comment
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE     # If user deleted, delete their comments
    )
    # The actual text content of the comment
    body = models.TextField("Comment")
    # Timestamp when the comment was created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # Show oldest comments first

    def __str__(self):
        """
        String representation for admin and debugging.
        """
        body_preview = (self.body[:75] + '...') if len(self.body) > 75 else self.body
        return f'Comment by {self.author.username} on "{self.video.title}": "{body_preview}"'