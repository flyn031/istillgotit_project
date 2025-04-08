# players/forms.py
from django import forms
# --- Import all models needed for forms in this file ---
from .models import PlayerProfile, VideoUpload, Comment

# --- Form for Editing PlayerProfile ---
class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = PlayerProfile
        fields = ['bio', 'date_of_birth', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }
        help_texts = {
            'avatar': 'Upload a profile picture (Optional). Current image will be replaced if you upload a new one.',
        }


# --- Form for Uploading Videos ---
class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = VideoUpload
        fields = ['title', 'description', 'video_file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional description...'}),
            'video_file': forms.ClearableFileInput(attrs={'accept': 'video/*'})
        }
        help_texts = {
            'video_file': 'Select a video file (e.g., mp4, mov).',
        }


# --- ADD Form for Submitting Comments ---
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment # Use the Comment model
        # Only include the 'body' field, as 'video' and 'author' will be set in the view
        fields = ['body']

        # Customize the widget for the comment body
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 3, # Make the text area smaller than default
                'placeholder': 'Add your comment...',
                'aria-label': 'Comment body' # For accessibility
            }),
        }
        # Remove the default label for the body field as the placeholder is enough
        labels = {
            'body': '',
        }
# --- END Comment Form ---