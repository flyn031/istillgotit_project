# players/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from django.db.models import F, Sum, Avg # Import Sum and Avg (already there)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone # Import timezone (already there)
from datetime import timedelta # Import timedelta (already there)
# from django.db.models.functions import Cast # No longer needed for stat_value_numeric if using the new field
from django.db.models import DecimalField # Import DecimalField (already there)
from django.db.models import Count # Import Count (already there)
from django.db.models import Q # Import Q (already there)


# Import Models
from .models import (
    PlayerProfile, VideoUpload, Comment, PhysicalStat,
    Match, SoccerMatchStat, CricketMatchStat, RugbyMatchStat,
    Subscription, ProfileView,
    VideoRating # <-- Import the new VideoRating model
)
# Import Forms
from .forms import (
    PlayerProfileForm, VideoUploadForm, CommentForm, CustomUserCreationForm,
    PhysicalStatForm, MatchForm,
    SoccerMatchStatForm, CricketMatchStatForm, RugbyMatchStatForm
)

# Define the view limit for free users per month
FREE_PROFILE_VIEW_LIMIT_PER_MONTH = 3

# --- Signup View (Unchanged) ---
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Use transaction.atomic to ensure both user and profile are created
            with transaction.atomic():
                PlayerProfile.objects.create(user=user) # Create profile upon signup
                # Create a default 'free' subscription for the new user
                Subscription.objects.create(user=user, user_type='free')
            login(request, user)
            messages.success(request, "Account created! Please complete your profile.")
            return redirect('players:profile_edit') # Redirect to profile edit after signup
        else: messages.error(request, "Please correct the errors below.")
    else: form = CustomUserCreationForm()
    return render(request, 'players/signup.html', {'form': form})


# --- Homepage View (Unchanged for level display - level is accessed in template) ---
def home_view(request):
    # --- Hybrid Featured Videos Logic (Keep existing) ---
    NUM_ADMIN_PICKS = 3
    NUM_POPULAR = 6
    MAX_TOTAL_VIDEOS = 6

    # Note: select_related('player_profile__user') is good for efficiency
    admin_featured_videos = list(VideoUpload.objects.filter(
        is_featured=True
    ).select_related('player_profile__user').order_by('-uploaded_at')[:NUM_ADMIN_PICKS])

    admin_featured_ids = [v.id for v in admin_featured_videos]
    popular_needed = MAX_TOTAL_VIDEOS - len(admin_featured_ids)

    popular_videos = []
    if popular_needed > 0:
        # Note: select_related('player_profile__user') is good for efficiency
        # Ordering by view_count is relevant here
        popular_videos = list(VideoUpload.objects.exclude(
            id__in=admin_featured_ids
        ).select_related('player_profile__user').order_by('-view_count', '-uploaded_at')[:popular_needed])

    featured_videos = admin_featured_videos + popular_videos
    # --- End Hybrid Featured Videos Logic ---

    # --- Freemium/Subscription Logic for Dashboard ---
    is_premium = False
    can_view_more_profiles = True
    profiles_viewed_this_month = 0
    # Fetch profiles efficiently, only getting data needed for the list view
    # Note: select_related('user') is essential here
    player_profiles_for_display = PlayerProfile.objects.select_related('user').filter(
        user__is_active=True # Only show active users
    ).order_by('user__username') # Order by username

    stat_rankings = {} # Dictionary to hold calculated stat rankings

    if request.user.is_authenticated:
        # *** Use get_or_create for Subscription ***
        subscription, created = Subscription.objects.get_or_create(user=request.user, defaults={'user_type': 'free'})
        is_premium = subscription.is_premium()

        if not is_premium:
            one_month_ago = timezone.now() - timedelta(days=30)
            profiles_viewed_this_month = ProfileView.objects.filter(
                user=request.user,
                viewed_at__gte=one_month_ago
            ).count()

            if profiles_viewed_this_month >= FREE_PROFILE_VIEW_LIMIT_PER_MONTH:
                can_view_more_profiles = False

        # --- Stat Ranking Logic (Only for Premium/Scout users) ---
        # Only fetch rankings if the user is premium
        if is_premium:
            # Note: Rankings require data in the stat_value_numeric field for Physical Stats
            # and players to have associated Match and MatchStat entries for aggregated stats.
            # Ensure your data entry forms/views populate stat_value_numeric or that you have data migrations.

            # Physical Stat Rankings (Using the new stat_value_numeric field)
            # Filter for entries where stat_value_numeric is NOT NULL for reliable sorting
            physical_stat_base_query = PhysicalStat.objects.filter(stat_value_numeric__isnull=False)

            # 100m Sprint (Lower value is better)
            try:
                 sprint_rankings = physical_stat_base_query.filter(
                     stat_name='100m Sprint'
                 ).order_by('stat_value_numeric')[:10].select_related('player_profile__user') # Get top 10
                 if sprint_rankings.exists():
                     stat_rankings['100m Sprint (Top 10)'] = sprint_rankings
            except Exception as e:
                 print(f"Error fetching sprint rankings: {e}")


            # Vertical Jump (Higher value is better)
            try:
                 vertical_jump_rankings = physical_stat_base_query.filter(
                     stat_name='Vertical Jump'
                 ).order_by('-stat_value_numeric')[:10].select_related('player_profile__user') # Get top 10
                 if vertical_jump_rankings.exists():
                     stat_rankings['Vertical Jump (Top 10)'] = vertical_jump_rankings
            except Exception as e:
                 print(f"Error fetching vertical jump rankings: {e}")

             # Broad Jump (Higher value is better)
            try:
                 broad_jump_rankings = physical_stat_base_query.filter(
                     stat_name='Broad Jump'
                 ).order_by('-stat_value_numeric')[:10].select_related('player_profile__user') # Get top 10
                 if broad_jump_rankings.exists():
                     stat_rankings['Broad Jump (Top 10)'] = broad_jump_rankings
            except Exception as e:
                 print(f"Error fetching broad jump rankings: {e}")


            # Aggregated Match Stat Rankings (Summing across matches)
            # Filter for PlayerProfiles that have at least one match stat entry for the relevant sport
            soccer_players_with_stats = PlayerProfile.objects.filter(
                 soccer_match_stats__isnull=False
             )
            cricket_players_with_stats = PlayerProfile.objects.filter(
                 cricket_match_stats__isnull=False
             )
            rugby_players_with_stats = PlayerProfile.objects.filter(
                 rugby_match_stats__isnull=False
             )


            # Soccer Goals (Higher is better)
            try:
                soccer_goal_rankings_query = soccer_players_with_stats.annotate(
                    total_goals=Sum('soccer_match_stats__goals') # Sum goals from related SoccerMatchStats
                ).order_by('-total_goals') # Order by total goals descending
                if soccer_goal_rankings_query.exists():
                     stat_rankings['Total Soccer Goals (Top 10)'] = soccer_goal_rankings_query[:10].select_related('user')
            except Exception as e:
                 print(f"Error fetching soccer goals rankings: {e}")

            # Cricket Runs (Higher is better)
            try:
                cricket_runs_rankings_query = cricket_players_with_stats.annotate(
                    total_runs=Sum('cricket_match_stats__runs_scored')
                ).order_by('-total_runs')
                if cricket_runs_rankings_query.exists():
                     stat_rankings['Total Cricket Runs (Top 10)'] = cricket_runs_rankings_query[:10].select_related('user')
            except Exception as e:
                 print(f"Error fetching cricket runs rankings: {e}")

             # Cricket Wickets (Higher is better)
            try:
                cricket_wickets_rankings_query = cricket_players_with_stats.annotate(
                    total_wickets=Sum('cricket_match_stats__wickets_taken')
                ).order_by('-total_wickets')
                if cricket_wickets_rankings_query.exists():
                     stat_rankings['Total Cricket Wickets (Top 10)'] = cricket_wickets_rankings_query[:10].select_related('user')
            except Exception as e:
                 print(f"Error fetching cricket wickets rankings: {e}")

            # Rugby Tries (Higher is better)
            try:
                rugby_tries_rankings_query = rugby_players_with_stats.annotate(
                    total_tries=Sum('rugby_match_stats__tries')
                ).order_by('-total_tries')
                if rugby_tries_rankings_query.exists():
                     stat_rankings['Total Rugby Tries (Top 10)'] = rugby_tries_rankings_query[:10].select_related('user')
            except Exception as e:
                 print(f"Error fetching rugby tries rankings: {e}")

             # Rugby Tackles (Higher is better)
            try:
                rugby_tackles_rankings_query = rugby_players_with_stats.annotate(
                    total_tackles=Sum('rugby_match_stats__tackles_made')
                ).order_by('-total_tackles')
                if rugby_tackles_rankings_query.exists():
                     stat_rankings['Total Rugby Tackles (Top 10)'] = rugby_tackles_rankings_query[:10].select_related('user')
            except Exception as e:
                 print(f"Error fetching rugby tackles rankings: {e}")


            # You can add more rankings here following similar patterns.

    # --- End Freemium/Subscription Logic ---

    context = {
        'featured_videos': featured_videos,
        'player_profiles_for_display': player_profiles_for_display, # These objects will have the new 'player_level' property
        'is_premium': is_premium,
        'can_view_more_profiles': can_view_more_profiles,
        'profiles_viewed_this_month': profiles_viewed_this_month,
        'view_limit': FREE_PROFILE_VIEW_LIMIT_PER_MONTH,
        'stat_rankings': stat_rankings, # Pass stat rankings for premium users
    }

    return render(request, 'players/home.html', context)


# --- Profile Detail View (Unchanged for level display - level is accessed in template) ---
@login_required
def profile_detail_view(request, pk=None):
    profile_to_view = None
    is_own_profile = False

    if pk:
        # Note: select_related('user') is good for efficiency
        profile_to_view = get_object_or_404(PlayerProfile.objects.select_related('user'), pk=pk)
        is_own_profile = (request.user == profile_to_view.user)
    else:
        try:
            profile_to_view = request.user.player_profile # This object will have the new 'player_level' property
            is_own_profile = True
        except PlayerProfile.DoesNotExist:
            messages.warning(request, "Please complete your player profile.")
            return redirect('players:profile_edit')

    # --- Freemium/Subscription/Profile View Tracking Logic (Keep existing) ---
    if request.user.is_authenticated and not is_own_profile:
        subscription, created = Subscription.objects.get_or_create(user=request.user, defaults={'user_type': 'free'})
        is_premium_viewer = subscription.is_premium()

        if not is_premium_viewer:
            one_month_ago = timezone.now() - timedelta(days=30)
            profiles_viewed_this_month = ProfileView.objects.filter(
                user=request.user,
                viewed_at__gte=one_month_ago
            ).count()
            can_view_more_profiles = profiles_viewed_this_month < FREE_PROFILE_VIEW_LIMIT_PER_MONTH

            already_viewed_this_month = ProfileView.objects.filter(
                user=request.user,
                player_profile=profile_to_view,
                viewed_at__gte=one_month_ago
            ).exists()

            if not is_premium_viewer and not is_own_profile and not already_viewed_this_month:
                 ProfileView.objects.create(user=request.user, player_profile=profile_to_view)


            context = {
                'profile': profile_to_view, # Pass the profile object with the new property
                'is_own_profile': is_own_profile,
                'is_premium_viewer': is_premium_viewer,
                'can_view_more_profiles': can_view_more_profiles,
                'profiles_viewed_this_month': profiles_viewed_this_month,
                'view_limit': FREE_PROFILE_VIEW_LIMIT_PER_MONTH,
            }
            context.update(get_profile_data_context(profile_to_view)) # Helper passes videos etc.

        else: # Viewer IS premium/scout
             context = {
                'profile': profile_to_view, # Pass the profile object with the new property
                'is_own_profile': is_own_profile,
                'is_premium_viewer': is_premium_viewer,
                'can_view_more_profiles': True, # Premium users can view unlimited profiles
             }
             context.update(get_profile_data_context(profile_to_view)) # Helper passes videos etc.

    else: # Viewing own profile or anonymous (though view is @login_required)
         context = {
            'profile': profile_to_view, # Pass the profile object with the new property
            'is_own_profile': is_own_profile,
            'is_premium_viewer': True, # Assume own profile view is unrestricted
            'can_view_more_profiles': True,
         }
         context.update(get_profile_data_context(profile_to_view)) # Helper passes videos etc.


    context['is_viewer_scout'] = request.user.is_authenticated and request.user.groups.filter(name='Scouts').exists()


    return render(request, 'players/profile_detail.html', context)

# Helper function to get common profile data (stats, videos, etc.)
# (Unchanged for level display - videos objects will have the new level property)
def get_profile_data_context(profile):
     # Note: prefetch_related('comments__author') is good for efficiency
     user_videos = profile.videos.prefetch_related('comments__author').all().order_by('-uploaded_at') # Video objects will have the new 'level' and 'average_rating' properties
     physical_stats = profile.physical_stats.all().order_by('-date_recorded')
     matches = Match.objects.filter(player_profile=profile).order_by('-match_date')

     matches = matches.prefetch_related('soccer_stats', 'cricket_stats', 'rugby_stats')

     for match in matches:
         if match.sport == 'Soccer': match.performance_stats = getattr(match, 'soccer_stats', None)
         elif match.sport == 'Cricket': match.performance_stats = getattr(match, 'cricket_stats', None)
         elif match.sport == 'Rugby': match.performance_stats = getattr(match, 'rugby_stats', None)
         else: match.performance_stats = None

     # --- Calculate Aggregated Stats for the profile being viewed (Keep existing) ---
     aggregated_stats = {}

     total_matches_count = matches.count()
     aggregated_stats['total_matches'] = total_matches_count

     if profile.matches_recorded.filter(sport='Soccer').exists():
         soccer_stats = SoccerMatchStat.objects.filter(player_profile=profile).aggregate(
             total_minutes_played=Sum('minutes_played'),
             total_goals=Sum('goals'),
             total_assists=Sum('assists'),
             total_shots=Sum('shots'),
             total_tackles=Sum('tackles_made'),
             total_soccer_matches=Count('id')
         )
         aggregated_stats['soccer'] = soccer_stats
         if soccer_stats['total_soccer_matches'] and soccer_stats['total_soccer_matches'] > 0:
              aggregated_stats['soccer']['avg_minutes_per_match'] = (soccer_stats['total_minutes_played'] or 0) / soccer_stats['total_soccer_matches']
              aggregated_stats['soccer']['avg_goals_per_match'] = (soccer_stats['total_goals'] or 0) / soccer_stats['total_soccer_matches']
              aggregated_stats['soccer']['avg_assists_per_match'] = (soccer_stats['total_assists'] or 0) / soccer_stats['total_soccer_matches']


     if profile.matches_recorded.filter(sport='Cricket').exists():
         cricket_stats = CricketMatchStat.objects.filter(player_profile=profile).aggregate(
             total_runs_scored=Sum('runs_scored'),
             total_wickets_taken=Sum('wickets_taken'),
             total_catches_taken=Sum('catches_taken'),
             total_overs_bowled=Sum('overs_bowled'),
             total_cricket_matches=Count('id')
         )
         aggregated_stats['cricket'] = cricket_stats
         if cricket_stats['total_cricket_matches'] and cricket_stats['total_cricket_matches'] > 0:
              aggregated_stats['cricket']['avg_runs_per_match'] = (cricket_stats['total_runs_scored'] or 0) / cricket_stats['total_cricket_matches']
              aggregated_stats['cricket']['avg_wickets_per_match'] = (cricket_stats['total_wickets_taken'] or 0) / cricket_stats['total_cricket_matches']


     if profile.matches_recorded.filter(sport='Rugby').exists():
         rugby_stats = RugbyMatchStat.objects.filter(player_profile=profile).aggregate(
             total_tries=Sum('tries'),
             total_tackles_made=Sum('tackles_made'),
             total_carries=Sum('carries'),
             total_metres_carried=Sum('metres_carried'),
             total_rugby_matches=Count('id')
         )
         aggregated_stats['rugby'] = rugby_stats
         if rugby_stats['total_rugby_matches'] and rugby_stats['total_rugby_matches'] > 0:
             aggregated_stats['rugby']['avg_tries_per_match'] = (rugby_stats['total_tries'] or 0) / rugby_stats['total_rugby_matches']
             aggregated_stats['rugby']['avg_tackles_per_match'] = (rugby_stats['total_tackles_made'] or 0) / rugby_stats['total_rugby_matches']


     return {
        'user_videos': user_videos, # These objects will have the new 'level' and 'average_rating' properties
        'physical_stats': physical_stats,
        'matches': matches,
        'aggregated_stats': aggregated_stats,
     }


# --- Video Detail View (View count logic already exists, unchanged) ---
def video_detail_view(request, pk):
    # Note: select_related('player_profile__user') is good for efficiency
    video = get_object_or_404(
        VideoUpload.objects.select_related('player_profile__user'),
        pk=pk
    )
    # This line increments the view count using F() - keep it as is
    # Note: This increments on every page load. For unique views, you'd need
    # more complex logic (sessions, cookies, or a dedicated view tracking model).
    VideoUpload.objects.filter(pk=pk).update(view_count=F('view_count') + 1)

    comment_form = CommentForm()
    if request.method == 'POST' and 'submit_comment' in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
        elif video.allow_comments:
            submitted_form = CommentForm(request.POST)
            if submitted_form.is_valid():
                new_comment = submitted_form.save(commit=False)
                new_comment.author = request.user
                new_comment.video = video
                new_comment.save()
                messages.success(request, "Comment added.")
                # Use reverse with args for redirect
                return redirect(reverse('players:video_detail', args=[video.pk]))
            else:
                messages.error(request, "Invalid comment.")
        else:
            messages.error(request, "Comments disabled for this video.")

    # Note: select_related('author') is good for efficiency
    comments = video.comments.select_related('author').order_by('created_at')

    context = {
        'video': video, # This object will have the new 'level' and 'average_rating' properties
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'players/video_detail.html', context)

# --- Profile Edit View (Unchanged) ---
@login_required
def profile_edit_view(request):
    profile, created = PlayerProfile.objects.get_or_create(user=request.user)
    if created: messages.info(request, "Welcome! Please complete your profile.")
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('players:profile_detail') # Redirect to the user's own profile detail
        else: messages.error(request, 'Please correct the errors below.')
    else: form = PlayerProfileForm(instance=profile)
    return render(request, 'players/profile_edit.html', {'form': form, 'profile': profile})


# --- Video Upload View (Unchanged) ---
@login_required
def video_upload_view(request):
    try: profile = request.user.player_profile
    except PlayerProfile.DoesNotExist:
        messages.error(request, "Please complete your player profile before uploading videos.")
        return redirect('players:profile_edit')
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False); video.player_profile = profile; video.save()
            messages.success(request, f"Video '{video.title}' uploaded successfully!")
            return redirect('players:profile_detail') # Redirect to the user's own profile detail
        else: messages.error(request, 'Please correct the errors below.')
    else: form = VideoUploadForm()
    return render(request, 'players/video_upload.html', {'form': form, 'profile': profile})


# --- Add Physical Stat View (Unchanged) ---
@login_required
def add_physical_stat_view(request):
    try: profile = request.user.player_profile
    except PlayerProfile.DoesNotExist:
        messages.error(request, "Please complete your player profile first.")
        return redirect('players:profile_edit')
    if request.method == 'POST':
        form = PhysicalStatForm(request.POST)
        if form.is_valid():
            stat = form.save(commit=False); stat.player_profile = profile; stat.save()
            messages.success(request, f"Physical Stat '{stat.get_stat_name_display()}' added successfully!")
            return redirect('players:profile_detail') # Redirect to the user's own profile detail
        else: messages.error(request, "Please correct errors.")
    else: form = PhysicalStatForm()
    return render(request, 'players/add_physical_stat.html', {'form': form, 'profile': profile})


# --- Add Match Record View (Unchanged) ---
@login_required
def add_match_record_view(request):
    try: profile = request.user.player_profile
    except PlayerProfile.DoesNotExist:
        messages.error(request, "Please complete your player profile first.")
        return redirect('players:profile_edit')
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match_record = form.save(commit=False); match_record.player_profile = profile; match_record.sport = profile.primary_sport; match_record.save()
            messages.info(request, f"Match record created for {match_record.get_sport_display()}. Now add performance stats.")
            return redirect('players:add_performance_stat', match_id=match_record.id)
        else: messages.error(request, "Please correct errors in match details.")
    else: form = MatchForm()
    return render(request, 'players/add_match_record.html', {'form': form, 'profile': profile})

# --- Add Performance Stat View (Unchanged) ---
@login_required
@transaction.atomic
def add_performance_stat_view(request, match_id):
    try: profile = request.user.player_profile
    except PlayerProfile.DoesNotExist:
        messages.error(request, "Profile required."); return redirect('players:profile_edit')
    match = get_object_or_404(Match, id=match_id, player_profile=profile)
    FormClass, template_name = None, None
    if match.sport == 'Soccer': FormClass, template_name = SoccerMatchStatForm, 'players/add_soccer_performance.html'
    elif match.sport == 'Cricket': FormClass, template_name = CricketMatchStatForm, 'players/add_cricket_performance.html'
    elif match.sport == 'Rugby': FormClass, template_name = RugbyMatchStatForm, 'players/add_rugby_performance.html'
    else:
        messages.error(request, f"Performance stat tracking not implemented for sport: {match.get_sport_display()}"); return redirect('players:profile_detail')
    existing_stats = None; related_name = f"{match.sport.lower()}_stats"
    if hasattr(match, related_name): existing_stats = getattr(match, related_name, None)
    if request.method == 'POST':
        form = FormClass(request.POST, instance=existing_stats)
        if form.is_valid():
            perf_stat = form.save(commit=False); perf_stat.match = match; perf_stat.player_profile = profile; perf_stat.save()
            action_word = "updated" if existing_stats else "saved"
            messages.success(request, f"{match.get_sport_display()} performance stats {action_word} successfully!"); return redirect('players:profile_detail') # Redirect to the user's own profile detail
        else: messages.error(request, "Please correct the errors in the performance stats.")
    else: form = FormClass(instance=existing_stats)
    context = { 'match': match, 'profile': profile, 'form': form }; return render(request, template_name, context)


# --- Browse Profiles View (Unchanged for level display - level is accessed in template) ---
def browse_profiles_view(request):
    selected_sport = request.GET.get('sport', None)
    # Note: select_related('user') is good for efficiency
    profile_list_query = PlayerProfile.objects.select_related('user').filter(
        user__is_active=True
    ).order_by('user__username') # These objects will have the new 'player_level' property
    valid_sports = [choice[0] for choice in PlayerProfile.SPORT_CHOICES]
    if selected_sport and selected_sport in valid_sports:
        profile_list_query = profile_list_query.filter(primary_sport=selected_sport)
    paginator = Paginator(profile_list_query, 16)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    context = {
        'page_obj': page_obj, # The PlayerProfile objects in page_obj will have the new property
        'sport_choices': PlayerProfile.SPORT_CHOICES,
        'selected_sport': selected_sport,
    }
    return render(request, 'players/browse_profiles.html', context)

# --- Note: The login_view is missing, assuming it's handled elsewhere (e.g., django.contrib.auth.views)
# If you have a custom login view in this file, you'll need to ensure it's handled.