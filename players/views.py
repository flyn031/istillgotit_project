# players/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import PlayerProfile, VideoUpload, Comment
from .forms import PlayerProfileForm, VideoUploadForm, CommentForm

# --- User Signup View ---
def signup_view(request): # ... (no changes) ...
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(); PlayerProfile.objects.create(user=user); login(request, user)
            return redirect('home')
    else: form = UserCreationForm()
    return render(request, 'players/signup.html', {'form': form})

# --- Homepage View ---
def home_view(request): # ... (no changes) ...
    context = {}; return render(request, 'players/home.html', context)

# --- Profile Detail View ---
@login_required
def profile_detail_view(request):
    # --- Get the profile being viewed (based on logged-in user viewing their own) ---
    # If you wanted users to view OTHERS' profiles, you'd need a username/pk in the URL
    profile = get_object_or_404(PlayerProfile, user=request.user)

    # --- Handle Comment Form Submission ---
    comment_form = CommentForm()
    if request.method == 'POST':
        submitted_form = CommentForm(request.POST)
        if submitted_form.is_valid():
            video_id = request.POST.get('video_id')
            try:
                video = VideoUpload.objects.get(id=video_id, player_profile=profile)
            except VideoUpload.DoesNotExist: messages.error(request, "Video not found or invalid.")
            else:
                new_comment = submitted_form.save(commit=False)
                new_comment.author = request.user
                new_comment.video = video
                new_comment.save()
                messages.success(request, "Comment added successfully!")
                return redirect('players:profile_detail')
        else:
             messages.error(request, "Failed to add comment. Please check your input.")
             comment_form = submitted_form # Pass back form with errors (template needs update to show errors inline)

    # --- Prepare data for template ---
    user_videos = profile.videos.prefetch_related('comments', 'comments__author').all()

    # --- Check if the VIEWER is a scout ---
    # request.user is the user making the request (the viewer)
    # We check if they are authenticated AND belong to the 'Scouts' group
    is_viewer_scout = False # Default to False
    if request.user.is_authenticated:
        # The groups check requires accessing the user's groups manager
        if request.user.groups.filter(name='Scouts').exists():
            is_viewer_scout = True
    # --- END Scout Check ---

    context = {
        'profile': profile, # The profile being viewed
        'user_videos': user_videos,
        'comment_form': comment_form,
        'is_viewer_scout': is_viewer_scout, # Pass the flag to the template
    }
    return render(request, 'players/profile_detail.html', context)


# --- Profile Edit View ---
@login_required
def profile_edit_view(request): # ... (no changes) ...
    profile = get_object_or_404(PlayerProfile, user=request.user)
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save(); messages.success(request, 'Profile updated successfully!')
            return redirect('players:profile_detail')
        else: messages.error(request, 'Please correct the errors below.')
    else: form = PlayerProfileForm(instance=profile)
    context = {'form': form, 'profile': profile }
    return render(request, 'players/profile_edit.html', context)

# --- Video Upload View ---
@login_required
def video_upload_view(request): # ... (no changes) ...
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_instance = form.save(commit=False)
            try: profile = request.user.player_profile
            except PlayerProfile.DoesNotExist: messages.error(request, "Player profile not found."); return redirect('home')
            video_instance.player_profile = profile; video_instance.save()
            messages.success(request, f"Video '{video_instance.title}' uploaded successfully!")
            return redirect('players:profile_detail')
        else: messages.error(request, 'Please correct the errors below.')
    else: form = VideoUploadForm()
    context = {'form': form}; return render(request, 'players/video_upload.html', context)