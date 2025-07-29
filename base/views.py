
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rentals.models import Rental
from auth_app.models import Profile
from django.contrib.auth.models import User
from django.db.models import Q

@login_required
def live_search(r):
    query = r.GET.get('search', '')

    rentals = Rental.objects.all()
    if query:
        rentals = rentals.filter(
            Q(address__icontains=query) |
            Q(price__icontains=query) |
            Q(user__username__icontains=query)
        )

    return render(r, 'partials/rental_cards.html', {'rentals': rentals})

@login_required(login_url='login')
def profiles(r):
    profiles = Profile.objects.exclude(user=r.user)
    return render(r, 'secret/profiles.html', {'profiles': profiles})

@login_required(login_url='login')
def secret_profile(r, id):
    profile = Profile.objects.get(user_id=id)
    return render(r, 'secret/profile.html', {'profile': profile})

def landing(r):
    return render(r, 'landing.html')

@login_required(login_url='login')
def home(r):
    profiles = Profile.objects.all()
    profile = Profile.objects.get(user=r.user)
    current_user_profile = r.user.profile
    r_object = r

    search_query = r.GET.get('search', '')
    rentals_qs = Rental.objects.all().select_related('user', 'user__profile')

    if search_query:
        rentals_qs = rentals_qs.filter(
            Q(address__icontains=search_query) |
            Q(price__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    rentals = rentals_qs.select_related('user', 'user__profile')

    if r.method == 'POST':
        action = r.POST.get('follow')
        profile_id = r.POST.get('profile_id')
        profile_to_follow = get_object_or_404(Profile, id=profile_id)

        if action == 'unfollow':
            current_user_profile.follows.remove(profile_to_follow)
        elif action == 'follow':
            current_user_profile.follows.add(profile_to_follow)

        current_user_profile.save()
        return redirect('home-page')

    return render(r, 'base.html', {
        'rentals': rentals, 
        'profiles': profiles,
        'profile': profile,
        'search_query': search_query
    })

def search(r):
    rentals = profiles = searched = None
    current_user_profile = r.user.profile
    profile = get_object_or_404(Profile, user=r.user)

    if r.method == 'POST':
        # Rental Search
        if 'search-rentals' in r.POST:
            searched = r.POST.get('search-rentals')
            rentals = Rental.objects.filter(
                Q(address__icontains=searched) |
                Q(price__icontains=searched) |
                Q(user__username__icontains=searched)
            )
            return render(r, 'public/search.html', {
                'rentals': rentals,
                'searched': searched,
                'profile': profile
            })


        # Profile Search
        elif 'search-profiles' in r.POST:
            searched = r.POST.get('search-profiles')
            profiles = Profile.objects.filter(
                Q(user__username__icontains=searched) |
                Q(address__icontains=searched)
            )

            # Follow/unfollow handling
            action = r.POST.get('follow')
            profile_id = r.POST.get('profile_id')
            if profile_id:
                profile_to_follow = get_object_or_404(Profile, id=profile_id)
                if action == 'follow':
                    current_user_profile.follows.add(profile_to_follow)
                elif action == 'unfollow':
                    current_user_profile.follows.remove(profile_to_follow)
                current_user_profile.save()

            return render(r, 'public/search.html', {
                'profiles': profiles,
                'searched': searched,
                'profile': profile
            })

    return render(r, 'public/search.html')


