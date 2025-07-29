
from django.shortcuts import render, redirect, get_object_or_404
from .models import Rental
from payments.models import PaymentHistory
from auth_app.models import Profile
from django.contrib.auth.models import User
from base.modules import feca
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from django.db.models import Q


@login_required(login_url='login')
def landlords_page(r):
    current_user_profile = r.user.profile
    search_query = r.GET.get('search', '')
    landlords_qs = User.objects.filter(rental__isnull=False).distinct()

    if search_query:
        landlords_qs = landlords_qs.filter(
            Q(username__icontains=search_query) |
            Q(profile__address__icontains=search_query)
        )
    landlords = landlords_qs.select_related('profile')
    if r.method == 'POST':
        action = r.POST.get('follow')
        profile_id = r.POST.get('profile_id')
        profile_to_follow = get_object_or_404(Profile, id=profile_id)

        if action == 'unfollow':
            current_user_profile.follows.remove(profile_to_follow)
        elif action == 'follow':
            current_user_profile.follows.add(profile_to_follow)

        current_user_profile.save()
        return redirect('people-with-rooms')

    return render(r, 'rentals/landlords.html', {
        'with_rooms': landlords,
        'profile': current_user_profile,
        'search_query': search_query,
    })

@login_required(login_url='login')
def post_rental(r):
    if r.method == 'POST':
        image = r.FILES.get('image')
        place = r.POST.get('place')
        details = r.POST.get('details')
        price = r.POST.get('price')

        good_extentions = ['.png', '.jpeg', '.jpg']

        if feca.check(str(image), good_extentions):
            rental = Rental.objects.create(image=image, address=place, details=details, price=price, user=r.user)
            rental.save()
            return redirect('my-profile' + f"/{rental.user.username}") # should redirect to the profile page
        else:
            messages.info(r, f"File extention does not match {good_extentions} Please ensure that you are uploading an image file.")
            return redirect('post-rental')
    else:
        return render(r, 'rentals/post-rental.html')


@login_required(login_url='login')
def availabe_rentals(r):
    profiles = Profile.objects.all()
    profile = Profile.objects.get(user=r.user)
    current_user_profile = r.user.profile

    search_query = r.GET.get('search', '')
    rentals_qs = Rental.objects.all().select_related('user', 'user__profile')

    if search_query:
        rentals_qs = rentals_qs.filter(
            Q(address__icontains=search_query) |
            Q(price__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    rentals = rentals_qs.select_related('user', 'user__profile')
    rentals = rentals.filter(is_occupied=False)

    if r.method == 'POST':
        action = r.POST.get('follow')
        profile_id = r.POST.get('profile_id')
        profile_to_follow = get_object_or_404(Profile, id=profile_id)

        if action == 'unfollow':
            current_user_profile.follows.remove(profile_to_follow)
        elif action == 'follow':
            current_user_profile.follows.add(profile_to_follow)

        current_user_profile.save()
        return redirect('availabe-rentals')

    return render(r, "rentals/availabe_rentals.html", {
        'rentals': rentals, 
        'profiles': profiles,
        'profile': profile,
        'search_query': search_query
    })

@login_required(login_url='login')
def edit_rental(r, id): # ADD EDIT RENTAL LOGIC
    rental = Rental.objects.get(id=id)
    l_user = r.user.username
    if r.method == 'POST':
        if r.FILES.get('image') == None:
            rental.image = rental.image
            rental.price = r.POST.get('price')
            rental.address = r.POST.get('place')
            rental.details = r.POST.get('details')
            rental.user = rental.user
            rental.is_occupied = r.POST.get('occupied') == 'on'
            rental.save()
            print(r.POST)
        if r.FILES.get('image') != None:
            rental.image = r.FILES.get('image')
            rental.price = r.POST.get('price')
            rental.address = r.POST.get('place')
            rental.details = r.POST.get('details')
            rental.user = rental.user
            rental.is_occupied = r.POST.get('occupied') == 'on'
            rental.save()
            print(r.POST)
        messages.info(r, 'Successfully edited rental!')
        # return redirect('/edit-rental/' + str(rental.id)) # this one is erroring but the below alternative worked flawlessly
        return render(r, 'rentals/edit_rental.html', {'rental': rental, 'l_user': l_user})

    return render(r, 'rentals/edit_rental.html', {'rental': rental, 'l_user': l_user})

@login_required(login_url='login')
def u_sure_u_wanna_delete_your_rental(r, id):
    rental = Rental.objects.get(id=id)
    l_user = r.user.username
    return render(r, 'rentals/u_sure_u_wanna_delete_your_rental.html', {'rental': rental, 'l_user': l_user})

@login_required(login_url='login')
def delete_rental(r, id):
    rental = Rental.objects.get(id=id)
    if rental.user.username == r.user.username:
        rental.delete()
        return redirect('home-page')
    else:
        return render(r, 'public/uyaphapha.html')

login_required(login_url='login')
def rental_detail(r, id):
    rental = get_object_or_404(Rental, id=id)
    l_user = r.user.username
    return render(r, 'rentals/rental_detail.html', {'rental': rental, 'l_user': l_user})

@login_required(login_url='login')
def rented_rentals(r):
    rented = PaymentHistory.objects.filter(user=r.user)
    seen = set()
    rents_total = 0.00
    u_rentals = []
    for paid in rented:
        rents_total+=float(paid.rental.price)
    # u for unique
    for u_rental in rented:
        if u_rental.rental.id not in seen:
            seen.add(u_rental.rental.id)
            u_rentals.append(u_rental)

    return render(r, 'rentals/rented.html', {'rented': u_rentals, 'rents_total': rents_total})
