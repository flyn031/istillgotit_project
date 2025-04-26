# players/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import Avg, Sum # Import Avg and Sum for aggregation

# ===================
# Player Profile Model
# ===================
class PlayerProfile(models.Model):
    SPORT_CHOICES = [ ('Soccer', 'Soccer'), ('Cricket', 'Cricket'), ('Rugby', 'Rugby'), ('Other', 'Other/Unspecified'), ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player_profile')
    primary_sport = models.CharField("Primary Sport", max_length=50, choices=SPORT_CHOICES, default='Other', help_text="Select the main sport you play.")
    bio = models.TextField(blank=True, null=True, help_text="A short biography of the player.")
    date_of_birth = models.DateField("Date of Birth", blank=True, null=True)
    avatar = models.ImageField("Avatar", upload_to='avatars/', null=True, blank=True)
    contact_email = models.EmailField("Contact Email (for scouts)", max_length=254, blank=True, null=True, help_text="Optional: Provide an email address if you wish to be contacted by verified scouts.")

    city = models.CharField("City / Town", max_length=100, blank=True, null=True, help_text="Your current city or town.")
    country = models.CharField("Country", max_length=100, blank=True, null=True, help_text="The country you are based in.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        sport_display = self.get_primary_sport_display();
        location = f" ({self.city}, {self.country})" if self.city and self.country else ""
        return f"{self.user.username}'s ({sport_display}) Profile{location}"

    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'): return self.avatar.url
        return None # Or return path to default avatar

    # --- NEW CODE: Player Level Calculation Properties ---

    @property
    def total_videos_views(self):
        """Aggregates view counts from all associated videos."""
        # Use aggregate for efficiency
        aggregate_views = self.videos.aggregate(total_views=Sum('view_count'))
        return aggregate_views['total_views'] or 0

    @property
    def overall_average_rating(self):
        """Calculates the average rating across all associated videos."""
        # Aggregate the average rating of all ratings related to this player's videos
        # Assumes VideoRating model exists and is related via 'ratings' related_name on VideoUpload
        aggregate_rating = VideoRating.objects.filter(video__player_profile=self).aggregate(avg_score=Avg('score'))
        return round(aggregate_rating['avg_score'] or 0.0, 1) # Round to 1 decimal place

    @property
    def player_level(self):
        """Determines the player's level based on total views and average rating."""
        views = self.total_videos_views
        avg_rating = self.overall_average_rating

        # Define your level thresholds here
        if avg_rating >= 4.5 and views >= 10000:
            return "Elite"
        elif avg_rating >= 4.0 and views >= 5000:
            return "Platinum"
        elif avg_rating >= 3.5 and views >= 1000:
            return "Gold"
        elif avg_rating >= 3.0 or views >= 500:
            return "Silver"
        elif views >= 100:
            return "Bronze"
        else:
            return "Newbie"

    # --- END NEW CODE ---


# ===================
# Video Upload Model (MODIFIED - Added level calculation property)
# ===================
class VideoUpload(models.Model):
    player_profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField("Video File", upload_to='videos/')
    thumbnail = models.ImageField("Thumbnail Image", upload_to='videos/thumbnails/', null=True, blank=True, help_text="Optional: Upload a representative image for the video (e.g., JPG, PNG).")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    allow_comments = models.BooleanField("Allow Comments", default=True)
    is_featured = models.BooleanField("Admin Featured", default=False, help_text="Mark this video to feature it prominently (Admin only).")
    view_count = models.PositiveIntegerField("View Count", default=0, help_text="Number of times the video has been viewed.")

    # --- NEW CODE: Video Level Calculation Properties ---

    @property
    def average_rating(self):
        """Calculates the average rating for this specific video."""
        # Assumes VideoRating model exists and is related via 'ratings' related_name
        aggregate_rating = self.ratings.aggregate(avg_score=Avg('score'))
        return round(aggregate_rating['avg_score'] or 0.0, 1) # Round to 1 decimal place

    @property
    def level(self):
        """Determines the video's level based on views and average rating."""
        views = self.view_count
        avg_rating = self.average_rating

        # Define your level thresholds here
        if avg_rating >= 4.8 and views >= 5000:
            return "Viral Hit"
        elif avg_rating >= 4.5 and views >= 1000:
            return "Trending"
        elif avg_rating >= 4.0 or views >= 500:
            return "Popular"
        elif views >= 100 or avg_rating >= 3.0:
            return "Rising"
        else:
            return "Standard"

    # --- END NEW CODE ---

    class Meta: ordering = ['-uploaded_at']
    def __str__(self): return f"'{self.title}' by {self.player_profile.user.username}"

# ===============
# Comment Model (Unchanged)
# ===============
class Comment(models.Model):
    video = models.ForeignKey(VideoUpload, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField("Comment")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['created_at']
    def __str__(self):
        body_preview = (self.body[:75] + '...') if len(self.body) > 75 else self.body
        return f'Comment by {self.author.username} on "{self.video.title}": "{body_preview}"'


# --- NEW MODEL: Video Rating ---
class VideoRating(models.Model):
    """Represents a rating given by a user to a video."""
    video = models.ForeignKey(VideoUpload, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # The user who submitted the rating
    score = models.IntegerField("Rating Score (1-5)", validators=[MinValueValidator(1), MaxValueValidator(5)]) # Store the rating (e.g., 1 to 5 stars)
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure a user can only rate a specific video once
        unique_together = ('video', 'user')
        ordering = ['-rated_at']

    def __str__(self):
        return f"{self.user.username} rated '{self.video.title}' {self.score}/5"

# --- END NEW MODEL ---


# ==============================
# Physical Stat Model (Unchanged from your provided code)
# ==============================
class PhysicalStat(models.Model):
    STAT_NAME_CHOICES = [ ('Height', 'Height'), ('Weight', 'Weight'), ('Wingspan', 'Wingspan'), ('Hand Size', 'Hand Size'), ('50m Sprint', '50m Sprint'), ('100m Sprint', '100m Sprint'), ('40-Yard Dash', '40-Yard Dash'), ('10-Yard Split', '10-Yard Split'), ('Pro Agility Shuttle', 'Pro Agility Shuttle (5-10-5)'), ('3-Cone Drill', '3-Cone Drill (L-Drill)'), ('Vertical Jump', 'Vertical Jump'), ('Broad Jump', 'Broad Jump'), ('Beep Test Level', 'Beep Test Level'), ('Yo-Yo Test Level', 'Yo-Yo Intermittent Test Level'), ('Other', 'Other Test/Measurement'), ]
    UNIT_CHOICES = [ ('cm', 'cm'), ('m', 'm'), ('inches', 'inches'), ('feet', 'feet'), ('yards', 'yards'), ('kg', 'kg'), ('lbs', 'lbs'), ('stone', 'stone'), ('seconds', 'seconds'), ('minutes', 'minutes'), ('level', 'level'), ('reps', 'reps'), ('%', '%'), ('N/A', 'N/A'), ('Other', 'Other'), ]
    player_profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='physical_stats')
    stat_name = models.CharField("Statistic Name", max_length=50, choices=STAT_NAME_CHOICES, help_text="Select the standard test or measurement.")
    stat_value = models.CharField("Value (as text)", max_length=50, help_text="Enter the measurement value (e.g., 185, 6'1\", 4.52, 11.2).")
    stat_value_numeric = models.DecimalField(
        "Value (Numeric)",
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Numerical value for ranking/comparison (e.g., 185 for cm, 4.52 for seconds, 0.85 for m)."
    )
    stat_unit = models.CharField("Unit", max_length=20, choices=UNIT_CHOICES, blank=True, null=True, help_text="Select the appropriate unit.")
    date_recorded = models.DateField("Date Recorded", help_text="When this measurement/test was taken.")
    class Meta: ordering = ['-date_recorded', 'stat_name']; verbose_name = "Physical Stat"; verbose_name_plural = "Physical Stats"
    def __str__(self): unit = f" {self.get_stat_unit_display()}" if self.stat_unit else ""; return f"{self.player_profile.user.username} - {self.get_stat_name_display()}: {self.stat_value}{unit} ({self.date_recorded})"

# ============================================
# Match Context Model (Unchanged)
# ============================================
class Match(models.Model):
    player_profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='matches_recorded')
    sport = models.CharField("Sport", max_length=50, choices=PlayerProfile.SPORT_CHOICES)
    match_date = models.DateField("Match Date", default=timezone.now)
    opponent = models.CharField("Opponent", max_length=100, blank=True)
    competition = models.CharField("Competition/Level", max_length=100, blank=True, help_text="e.g., U18 League, County Championship, Friendly")
    season = models.CharField("Season", max_length=50, blank=True, help_text="e.g., 2024-2025")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    class Meta: ordering = ['-match_date']; verbose_name = "Match Record"; verbose_name_plural = "Match Records"
    def __str__(self): opponent_str = f" vs {self.opponent}" if self.opponent else ""; return f"{self.player_profile.user.username} - {self.get_sport_display()} Match on {self.match_date}{opponent_str}"

# ============================================
# Sport-Specific Performance Models (Unchanged)
# ============================================
class SoccerMatchStat(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='soccer_stats'); player_profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='soccer_match_stats'); position = models.CharField("Position Played", max_length=50, blank=True, help_text="e.g., CAM, CB, GK"); minutes_played = models.PositiveIntegerField("Minutes Played", default=0, validators=[MinValueValidator(0), MaxValueValidator(150)]); goals = models.PositiveIntegerField("Goals Scored", default=0); assists = models.PositiveIntegerField("Assists", default=0); shots = models.PositiveIntegerField("Total Shots", default=0); shots_on_target = models.PositiveIntegerField("Shots on Target", default=0); passes_attempted = models.PositiveIntegerField("Passes Attempted", default=0); passes_completed = models.PositiveIntegerField("Passes Completed", default=0); tackles_made = models.PositiveIntegerField("Tackles Made", default=0); interceptions = models.PositiveIntegerField("Interceptions", default=0); clearances = models.PositiveIntegerField("Clearances", default=0); dribbles_completed = models.PositiveIntegerField("Dribbles Completed", default=0); fouls_committed = models.PositiveIntegerField("Fouls Committed", default=0); yellow_cards = models.PositiveIntegerField("Yellow Cards", default=0, validators=[MaxValueValidator(2)]); red_cards = models.PositiveIntegerField("Red Cards", default=0, validators=[MaxValueValidator(1)])
    @property
    def pass_accuracy_percent(self):
        if self.passes_attempted and self.passes_attempted > 0: return round((self.passes_completed / self.passes_attempted) * 100, 1)
        return None
    @property
    def shots_on_target_percent(self):
        if self.shots and self.shots > 0: return round((self.shots_on_target / self.shots) * 100, 1)
        return None
    class Meta: verbose_name = "Soccer Match Stat"; verbose_name_plural = "Soccer Match Stats"
    def __str__(self): return f"Soccer Stats for {self.player_profile.user.username} in Match {self.match.id}"

class CricketMatchStat(models.Model):
    MATCH_FORMAT_CHOICES = [ ('Test', 'Test/Multi-Day'), ('ODI', 'ODI (50 Over)'), ('T20', 'T20'), ('Other', 'Other'), ]; BOWLING_TYPE_CHOICES = [ ('Pace', 'Pace'), ('Spin', 'Spin'), ('Mixed', 'Mixed'), ('None', 'Did not bowl'), ('Other', 'Other') ]; match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='cricket_stats'); player_profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='cricket_match_stats'); batting_order_position = models.PositiveIntegerField("Batting Pos.", null=True, blank=True); runs_scored = models.PositiveIntegerField("Runs Scored", default=0); balls_faced = models.PositiveIntegerField("Balls Faced", default=0); fours_hit = models.PositiveIntegerField("4s Hit", default=0); sixes_hit = models.PositiveIntegerField("6s Hit", default=0); not_out = models.BooleanField("Not Out?", default=False); bowling_type = models.CharField("Bowling Type", max_length=10, choices=BOWLING_TYPE_CHOICES, default='None', blank=True); overs_bowled = models.DecimalField("Overs Bowled", max_digits=4, decimal_places=1, default=0.0, help_text="e.g., 4.2 for 4 overs and 2 balls"); runs_conceded = models.PositiveIntegerField("Runs Conceded", default=0); wickets_taken = models.PositiveIntegerField("Wickets Taken", default=0); maidens_bowled = models.PositiveIntegerField("Maidens Bowled", default=0); dot_balls_bowled = models.PositiveIntegerField("Dot Balls Bowled", null=True, blank=True, default=0); catches_taken = models.PositiveIntegerField("Catches Taken", default=0); run_outs_effected = models.PositiveIntegerField("Run Outs Effected", default=0); stumpings = models.PositiveIntegerField("Stumpings (Wicketkeeper)", default=0)
    @property
    def strike_rate(self):
        if self.balls_faced and self.balls_faced > 0: return round((self.runs_scored / self.balls_faced) * 100, 1)
        return None
    @property
    def economy_rate(self):
        if self.overs_bowled and self.overs_bowled > 0:
            full_overs = int(self.overs_bowled); partial_balls = round((self.overs_bowled - full_overs) * 10); total_balls = (full_overs * 6) + partial_balls
            if total_balls > 0: return round((self.runs_conceded / total_balls) * 6, 2)
        return None
    class Meta: verbose_name = "Cricket Match Stat"; verbose_name_plural = "Cricket Match Stats"
    def __str__(self): unit = f" {self.get_stat_unit_display()}" if self.stat_unit else ""; return f"Cricket Stats for {self.player_profile.user.username} in Match {self.match.id}"

class RugbyMatchStat(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='rugby_stats'); player_profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='rugby_match_stats'); position = models.CharField("Position Played", max_length=50, blank=True, help_text="e.g., Flanker, Fly-Half"); minutes_played = models.PositiveIntegerField("Minutes Played", default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]); tries = models.PositiveIntegerField("Tries Scored", default=0); carries = models.PositiveIntegerField("Carries Made", default=0); metres_carried = models.PositiveIntegerField("Metres Carried", default=0); offloads = models.PositiveIntegerField("Offloads", default=0); tackles_made = models.PositiveIntegerField("Tackles Made", default=0); missed_tackles = models.PositiveIntegerField("Missed Tackles", default=0); turnovers_won = models.PositiveIntegerField("Turnovers Won", default=0); successful_kicks = models.PositiveIntegerField("Successful Kicks (Place)", default=0, help_text="Goals from Conversions and Penalties"); kicking_metres = models.PositiveIntegerField("Kicking Metres (From Hand)", default=0, blank=True, null=True); conversions = models.PositiveIntegerField("Conversions Made", default=0); penalties = models.PositiveIntegerField("Penalty Goals Made", default=0); drop_goals = models.PositiveIntegerField("Drop Goals Made", default=0)
    @property
    def tackle_success_percent(self):
        total_tackles = self.tackles_made + self.missed_tackles
        if total_tackles > 0: return round((self.tackles_made / total_tackles) * 100, 1)
        return None
    class Meta: verbose_name = "Rugby Match Stat"; verbose_name_plural = "Rugby Match Stats"
    def __str__(self): return f"Rugby Stats for {self.player_profile.user.username} in Match {self.match.id}"

# ==============================
# User Subscription Status (Unchanged)
# ==============================
class Subscription(models.Model):
    USER_TYPE_CHOICES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('scout', 'Scout'), # Example: Maybe scouts have a different subscription
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='free')
    # You could add fields like:
    # start_date = models.DateField(auto_now_add=True)
    # expiry_date = models.DateField(null=True, blank=True)
    # payment_status = models.CharField(max_length=50, default='pending')

    def is_premium(self):
        # Add logic here if premium is time-limited
        return self.user_type in ['premium', 'scout'] # Scouts are also 'premium' in this context

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

# ==============================
# Track Profile Views for Freemium Logic (Unchanged)
# ==============================
class ProfileView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile_views')
    player_profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='viewed_by') # Link to PlayerProfile
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Order by most recent views
        ordering = ['-viewed_at']
        # Optional: Add a unique constraint if a user can only view a profile once per specific period
        # unique_together = ('user', 'player_profile', 'date_recorded') # Example for daily limit

    def __str__(self):
        return f"{self.user.username} viewed {self.player_profile.user.username}'s profile at {self.viewed_at.strftime('%Y-%m-%d %H:%M')}"

# IMPORTANT: After saving this file, you need to make and run migrations!
# In your terminal from the project root:
# python manage.py makemigrations
# python manage.py migrate