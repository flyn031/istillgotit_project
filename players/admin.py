# players/admin.py
from django.contrib import admin
from django.utils.html import format_html # Import format_html
from .models import (
    PlayerProfile, VideoUpload, Comment, PhysicalStat, Match,
    SoccerMatchStat, CricketMatchStat, RugbyMatchStat, Subscription, ProfileView # Added Subscription, ProfileView
)

# --- Inline Admins (Unchanged) ---
class SoccerStatInline(admin.StackedInline): model = SoccerMatchStat; can_delete = False; verbose_name_plural = 'Soccer Stats'; fk_name = 'match'; extra = 0
class CricketStatInline(admin.StackedInline): model = CricketMatchStat; can_delete = False; verbose_name_plural = 'Cricket Stats'; fk_name = 'match'; extra = 0
class RugbyStatInline(admin.StackedInline): model = RugbyMatchStat; can_delete = False; verbose_name_plural = 'Rugby Stats'; fk_name = 'match'; extra = 0

# --- ModelAdmin Definitions ---

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'primary_sport', 'date_of_birth', 'updated_at')
    list_filter = ('primary_sport',)
    search_fields = ('user__username', 'user__email', 'contact_email')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'player_profile', 'sport', 'match_date', 'opponent')
    list_filter = ('sport', 'season', 'player_profile__primary_sport')
    search_fields = ('player_profile__user__username', 'opponent', 'competition')
    date_hierarchy = 'match_date'
    list_per_page = 25
    inlines = [SoccerStatInline, CricketStatInline, RugbyStatInline] # Added inlines here to allow adding stats when adding a Match

@admin.register(PhysicalStat)
class PhysicalStatAdmin(admin.ModelAdmin):
    list_display = ('player_profile', 'stat_name', 'stat_value', 'stat_value_numeric', 'stat_unit', 'date_recorded') # Added numerical field
    list_filter = ('stat_name', 'player_profile__primary_sport', 'date_recorded') # Added date_recorded filter
    search_fields = ('player_profile__user__username', 'stat_name', 'stat_value') # Added stat_value search
    list_per_page = 25
    date_hierarchy = 'date_recorded'

# Added Subscription and ProfileView to Admin
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'user__email')
    list_editable = ('user_type',) # Allow changing subscription type directly in list view

@admin.register(ProfileView)
class ProfileViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'player_profile', 'viewed_at')
    list_filter = ('viewed_at', 'user__subscription__user_type') # Filter by date and viewer's subscription type
    search_fields = ('user__username', 'player_profile__user__username')
    date_hierarchy = 'viewed_at' # Allow drilling down by date
    list_per_page = 25


@admin.register(SoccerMatchStat)
class SoccerMatchStatAdmin(admin.ModelAdmin):
    list_display = ('match', 'player_profile', 'position', 'minutes_played', 'goals', 'assists') # Kept display simple
    search_fields = ('player_profile__user__username', 'match__opponent', 'match__season')
    list_per_page = 25
    raw_id_fields = ('match', 'player_profile')

@admin.register(CricketMatchStat)
class CricketMatchStatAdmin(admin.ModelAdmin):
    # Removed match_format_override from list_display and list_filter for now to resolve the error
    # We can re-add it after confirming the field exists and is recognized.
    list_display = ('match', 'player_profile', 'runs_scored', 'wickets_taken', 'catches_taken')
    list_filter = ('match__sport', 'match__season', 'player_profile__primary_sport') # Using fields on the related Match/PlayerProfile
    search_fields = ('player_profile__user__username', 'match__opponent', 'match__season')
    list_per_page = 25
    raw_id_fields = ('match', 'player_profile')

@admin.register(RugbyMatchStat)
class RugbyMatchStatAdmin(admin.ModelAdmin):
    list_display = ('match', 'player_profile', 'position', 'tries', 'tackles_made', 'successful_kicks')
    search_fields = ('player_profile__user__username', 'match__opponent', 'match__season')
    list_per_page = 25
    raw_id_fields = ('match', 'player_profile')


# --- MODIFIED VideoUploadAdmin ---
@admin.register(VideoUpload)
class VideoUploadAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'player_profile',
        'thumbnail_preview', # Show thumbnail preview
        'uploaded_at',
        'view_count',
        'is_featured',
        'allow_comments'
    )
    list_filter = (
        'is_featured',
        'allow_comments',
        'player_profile__primary_sport'
    )
    search_fields = ('title', 'player_profile__user__username', 'description') # Added description search
    list_editable = (
        'is_featured',
        'allow_comments', # Allow editing allow_comments from the list view
    )
    readonly_fields = (
        'thumbnail_preview', # Show preview in form as well
        'view_count',
        'uploaded_at',
    )
    # Add thumbnail to the fields shown in the edit form
    fields = (
        'player_profile', 'title', 'description',
        'video_file', 'thumbnail', 'thumbnail_preview', # Add thumbnail field next to its preview
        'allow_comments', 'is_featured', 'view_count', 'uploaded_at'
     )

    # Function to display thumbnail in list_display and readonly_fields
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.thumbnail.url)
        return "(No thumbnail)"
    thumbnail_preview.short_description = 'Thumbnail Preview'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'video', 'created_at', '__str__') # Added __str__ for better display
    search_fields = ('author__username', 'video__title', 'body')
    list_filter = ('created_at', 'video__player_profile__primary_sport') # Filter comments by date or video owner's sport