from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CreateUserForm, ProfileForm, PostForm
from .models import UserProfile, Post


def home(request):
    posts = Post.objects.none()
    suggested = UserProfile.objects.none()

    if request.user.is_authenticated:
        me = request.user.profile
        following = me.following.all()
        posts = (
            Post.objects
            .filter(Q(author__profile__in=following) | Q(author=request.user))
            .select_related('author__profile')
        )
        # People you don't follow yet (new: powers the "Suggested people" panel)
        suggested = (
            UserProfile.objects
            .exclude(pk=me.pk)
            .exclude(pk__in=following)
            .select_related('user')
            .order_by('-created_at')[:4]
        )

    return render(request, 'main/home.html', {'posts': posts, 'suggested': suggested})


def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created. You can sign in now.')
            return redirect('login')
    else:
        form = CreateUserForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request, username):
    profile_user = get_object_or_404(UserProfile.objects.select_related('user'), user__username=username)
    posts = Post.objects.filter(author=profile_user.user).select_related('author__profile')
    is_following = request.user.profile.following.filter(pk=profile_user.pk).exists()
    return render(request, 'main/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'is_me': profile_user.user_id == request.user.id,
    })


@login_required
def edit_profile(request):
    profile_user = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile_user)
    return render(request, 'main/edit_profile.html', {'form': form})


def _back(request, fallback):
    """Redirect to a safe ?next= target if one was posted, else to the fallback."""
    target = request.POST.get('next')
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(target)
    return fallback


@login_required
@require_POST
def toggle_follow(request, username):
    me = request.user.profile
    person = get_object_or_404(UserProfile, user__username=username)
    fallback = redirect('profile', username=username)

    if person == me:
        return fallback

    if me.following.filter(id=person.id).exists():
        me.following.remove(person)
    else:
        me.following.add(person)

    return _back(request, fallback)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Posted.')
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'main/create_post.html', {'form': form})


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('profile', username=request.user.username)

@login_required
def search(request):
    q = request.GET.get('q', '').strip()
    people = []
    following_ids = set()

    if q:
        following_ids = set(request.user.profile.following.values_list('id', flat=True))
        people = (
            UserProfile.objects
            .filter(user__username__icontains=q)
            .select_related('user')
            .order_by('user__username')[:20]
        )

    return render(request, 'main/search.html', {
        'q': q, 'people': people, 'following_ids': following_ids,
    })