# players/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models

# Import models
from .models import (
    PlayerProfile, VideoUpload, Comment, PhysicalStat, Match,
    SoccerMatchStat, CricketMatchStat, RugbyMatchStat,
)

# --- MODIFIED: PlayerProfileForm ---
class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = PlayerProfile
        # Add city and country to fields
        fields = [
            'primary_sport', 'bio', 'date_of_birth', 'avatar',
            'city', 'country', # <-- Added location fields
            'contact_email'
        ]
        widgets = {
            'primary_sport': forms.Select(),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
            'avatar': forms.ClearableFileInput(),
            # Add widgets for location fields
            'city': forms.TextInput(attrs={'placeholder': 'e.g., London, Manchester'}),
            'country': forms.TextInput(attrs={'placeholder': 'e.g., United Kingdom, USA'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'Optional: email for scouts'}),
        }
        help_texts = {
            'primary_sport': 'Select your main sport.',
            'avatar': 'Upload a profile picture (Optional). Current image will be replaced if you upload a new one.',
            # Add help texts for location fields
            'city': 'The city or town where you are primarily based.',
            'country': 'The country where you are primarily based.',
            'contact_email': 'Only provide if you wish verified scouts to contact you.',
            'bio': 'Write a brief summary about your playing career, ambitions, etc.',
            'date_of_birth': 'Select your date of birth.',
        }

# --- VideoUploadForm ---
class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = VideoUpload
        fields = ['title', 'description', 'video_file', 'thumbnail', 'allow_comments']
        widgets = {
             'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional description...'}),
             'video_file': forms.ClearableFileInput(attrs={'accept': 'video/*'}),
             'thumbnail': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
        help_texts = {
            'video_file': 'Select a video file (e.g., mp4, mov).',
            'thumbnail': 'Optional: Upload an image (JPG, PNG) to represent this video.',
            'allow_comments': 'Allow other users to comment on this video?',
        }

# --- CommentForm ---
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
             'body': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add comment...', 'aria-label': 'Comment body'}),
        }
        labels = { 'body': '', }

# --- CustomUserCreationForm ---
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# --- Physical Stat Form ---
class PhysicalStatForm(forms.ModelForm):
    class Meta:
        model = PhysicalStat
        fields = ['stat_name', 'stat_value', 'stat_unit', 'date_recorded']
        widgets = {
            'stat_name': forms.Select(),
            'stat_value': forms.TextInput(attrs={'placeholder': 'Enter value (e.g., 185, 6\'1", 4.52)'}),
            'stat_unit': forms.Select(),
            'date_recorded': forms.DateInput(attrs={'type': 'date'}),
        }
        help_texts = {
            'stat_name': 'Select the standard test or measurement.',
            'stat_value': 'Enter the corresponding value or result.',
            'stat_unit': 'Select the unit.',
            'date_recorded': 'Date the measurement or test was performed.',
        }

# --- Match Context Form ---
class MatchForm(forms.ModelForm):
     class Meta:
         model = Match
         fields = ['match_date', 'opponent', 'competition', 'season']
         widgets = {
            'match_date': forms.DateInput(attrs={'type': 'date'}),
            'opponent': forms.TextInput(attrs={'placeholder': 'e.g., Team Rival FC'}),
            'competition': forms.TextInput(attrs={'placeholder': 'e.g., U18 League, Friendly'}),
            'season': forms.TextInput(attrs={'placeholder': 'e.g., 2024-2025'}),
         }
         help_texts = {
             'match_date': 'Date the match was played.',
             'opponent': 'Name of the opposing team (optional).',
             'competition': 'Name of the league, cup, or level (optional).',
             'season': 'The season this match belongs to (optional).',
         }

# --- Soccer Performance Form ---
class SoccerMatchStatForm(forms.ModelForm):
    class Meta:
        model = SoccerMatchStat
        exclude = ('match', 'player_profile')
        widgets = {field.name: forms.NumberInput(attrs={'min': '0', 'value': '0'})
                   for field in SoccerMatchStat._meta.get_fields()
                   if isinstance(field, models.PositiveIntegerField) and field.name not in ['id', 'match', 'player_profile']}
        widgets['position'] = forms.TextInput(attrs={'placeholder': 'e.g., CAM, CB'})
        widgets['yellow_cards'] = forms.NumberInput(attrs={'min':'0', 'max': '2', 'value': '0'})
        widgets['red_cards'] = forms.NumberInput(attrs={'min':'0', 'max': '1', 'value': '0'})

# --- Cricket Performance Form ---
class CricketMatchStatForm(forms.ModelForm):
    class Meta:
        model = CricketMatchStat
        exclude = ('match', 'player_profile')
        widgets = {field.name: forms.NumberInput(attrs={'min': '0', 'value': '0'})
                   for field in CricketMatchStat._meta.get_fields()
                   if isinstance(field, models.PositiveIntegerField) and field.name not in ['id', 'match', 'player_profile']}
        widgets['match_format_override'] = forms.Select()
        widgets['bowling_type'] = forms.Select()
        widgets['not_out'] = forms.CheckboxInput()
        widgets['overs_bowled'] = forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'value': '0.0'})

# --- Rugby Performance Form ---
class RugbyMatchStatForm(forms.ModelForm):
     class Meta:
        model = RugbyMatchStat
        exclude = ('match', 'player_profile')
        widgets = {field.name: forms.NumberInput(attrs={'min': '0', 'value': '0'})
                   for field in RugbyMatchStat._meta.get_fields()
                   if isinstance(field, models.PositiveIntegerField) and field.name not in ['id', 'match', 'player_profile']}
        widgets['position'] = forms.TextInput(attrs={'placeholder': 'e.g., Fly-half, Flanker'})