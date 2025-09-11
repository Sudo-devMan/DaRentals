
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rentals.models import Rental, RentalImage
from auth_app.models import Profile
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse

def fluffhome(r):
    return render(r, 'noFluff/home.html')

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

def home(r):
    landlords = User.objects.filter(rental__isnull=False).distinct()
    landlords = landlords.select_related('profile')
    landlords_count = Rental.objects.values('user').distinct().count()
    rooms_count = Rental.objects.filter(type_of_rental='room').count()
    apartments_count = Rental.objects.filter(type_of_rental='apartment').count()
    business_count = Rental.objects.filter(type_of_rental='business_property').count()
    student_dorms_count = Rental.objects.filter(type_of_rental='student_dorm').count()
    popular_count = Rental.objects.filter(is_popular=True).count()

    search_query = r.GET.get('search', '')
    rentals_qs = Rental.objects.all().select_related('user', 'user__profile')[:10]

    rentals_list = []

    class TheRental:
        def __init__(self, rental, images):
            self.rental = rental
            self.images = []

    for rental in rentals_qs:
        images = RentalImage.objects.filter(rental=rental)
        rental_obj = TheRental(rental, images)
        rentals_list.append(
            rental_obj
        )

    if search_query:
        rentals_qs = rentals_qs.filter(
            Q(address__icontains=search_query) |
            Q(price__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    rentals = rentals_qs.select_related('user', 'user__profile')


    context = {
        'rentals': rentals,
        'rooms_count': rooms_count,
        'student_dorms_count': student_dorms_count,
        'landlords_count': landlords_count,
        'business_count': business_count,
        'apartments_count': apartments_count,
        'search_query': search_query,
        'landlords': landlords,
        'popular_count': popular_count,
        'rental_obj': rental_obj
    }

    return render(r, 'themeforest/index.html', context=context)

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

def terms_of_use(r):
    return render(r, "public/ToU.html")