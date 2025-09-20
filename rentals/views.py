
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Rental, RentalImage, RentalRating
from payments.models import PaymentHistory
from auth_app.models import Profile
from django.contrib.auth.models import User
from base.modules import feca
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from django.db.models import Q, Count
from django.db import models
import math
from django.http import HttpResponse, JsonResponse

def all_rentals(r):
    rentals = Rental.objects.all()
    return render(r, 'themeforest/properties.html', {'rentals': rentals})

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
        return redirect(r.META.get("HTTP_REFERER"))

    return render(r, 'rentals/landlords.html', {
        'with_rooms': landlords,
        'profile': current_user_profile,
        'search_query': search_query,
    })    

@login_required(login_url='login')
def post_rental(r):
    if r.method == 'POST':
        images = r.FILES.getlist('image')
        address = r.POST.get('address')
        details = r.POST.get('details')
        price = r.POST.get('price')
        type_of_rental = r.POST.get('type')
        size = r.POST.get('size')
        baths = int(math.fabs(int(r.POST.get('baths'))))
        beds = int(math.fabs(int(r.POST.get('beds'))))

        rental = Rental.objects.create(user=r.user,
                                        address=address,
                                        details=details,
                                        price=price,
                                        size=size,
                                        type_of_rental=type_of_rental,
                                        baths=baths,
                                        beds=beds)

        good_extentions = ['.png', '.jpeg', '.jpg']

        if len(images) <= 5 and len(images) > 0:
            rental.save()
            for image in images:
                image_as_string = str(image)
                # print("Image:", image_as_string)
                # print("Does the extention match:", feca.check(image_as_string, good_extentions))
                # print(image_as_string.index('.')) # ------ This is when I thought my algorithm was acting up
                if feca.check(image_as_string, good_extentions):
                    new_image = RentalImage(image=image, rental=rental)
                    new_image.save()
                    rental.images.add(new_image)
                else:
                    messages.error(r, f"{image} is not a valid image file. Should have: {good_extentions}")
                    return redirect('post-rental')
            rental.save()
            messages.success(r, "Rental successfully posted!")
            return redirect('home')
        else:
            messages.error(r, "Image count should be between 5")
            return redirect('post-rental')


    else:
        return render(r, 'rentals/post-rental.html')

@login_required(login_url='login')
def edit_rental(r, id):
    rental = get_object_or_404(Rental, user=r.user, id=id)
    if r.method == 'POST':
        deleteImage = r.POST.get('deleteImage')
        if deleteImage:
            print("There is an image:",r.POST.get('deleteImage'), "Type:", type(r.POST.get('deleteImage')))
            if rental.images.all().count() == 1:
                messages.error(r, "You cannot delete all images wena!!")
                return redirect(reverse('edit-rental', kwargs={'id': rental.id}))
            get_object_or_404(RentalImage, id=int(deleteImage)).delete()
            print("Delete image name:",r.POST.get('deleteImage'),"| Type:", type(r.POST.get('deleteImage')))
            print(f"Post data: {r.POST}")
            messages.warning(r, "Successfully deleted image")
            return redirect(reverse('edit-rental', kwargs={'id': rental.id}))
        else:
            images = r.FILES.getlist('image')
            address = r.POST.get('address')
            details = r.POST.get('details')
            price = r.POST.get('price')
            type_of_rental = r.POST.get('type')
            size = r.POST.get('size')
            baths = str(int(math.fabs(int(r.POST.get('baths')))))
            beds = str(int(math.fabs(int(r.POST.get('beds')))))

            print("Type of price:", type(price), "Value:", price)

            rental.address = address
            rental.details = details
            rental.price = price
            rental.type_of_rental = type_of_rental
            rental.size = size
            rental.baths = baths
            rental.beds = beds
            rental.is_occupied = True if r.POST.get("is_occupied") == "on" else False
            rental.is_popular = True if r.POST.get("is_popular") == "on" else False
            rental.save()

            # CREATE DISPLAY OF ALL IMAGES IN RENTAL. ALLOW DELETION OF INDIVIDUAL IMAGES.
            # ALLOW ADDITION OF IMAGE VIA CUSTOM INPUT FIELD INLINE WITH THE OTHER RENTAL IMAGES

            good_extentions = ['.png', '.jpeg', '.jpg']
            # r.user.profile.is_premium ----- REPLACE TRUE WITH THIS
            if len(images) > 0 and len(images) <= 5 and rental.images.all().count() <= 5:
                if 10 > 78: # if user is premium (add the premium stuff at a later stage)
                    for image in images:
                        image_as_string = str(image)
                        if feca.check(image_as_string, good_extentions):
                            new_image = RentalImage(image=image, rental=rental)
                            new_image.save()
                            rental.images.add(new_image)
                        else:
                            messages.error(r, f"{image} is not a valid image file. Should have: {good_extentions}")
                            return redirect(reverse('edit-rental', kwargs={'id': rental.id}))
                    rental.save()
                    messages.success(r, "Rental successfully editted!")
                    return redirect('home')
                else:
                    if rental.images.all().count() > 5:
                        messages.error(r, "You have a maximum of 5 image uploads")
                        return redirect(reverse('edit-rental', kwargs={'id': rental.id}))
                    else:
                        for image in images:
                            image_as_string = str(image)
                            if feca.check(image_as_string, good_extentions):
                                new_image = RentalImage(image=image, rental=rental)
                                new_image.save()
                                if rental.images.all().count() < 5 and len(images) < 5:
                                    rental.images.add(new_image)
                                elif rental.images.all().count() > 5:
                                    length = rental.images.all().count()
                                    removed = 0
                                    while length > 5:
                                        rental.images.exclude(id__in=rental.images.all().order_by('id')[:5].values_list('id', flat=True)).delete()
                                        rental.images.first().delete()
                                        removed += 1
                                    messages.error(r, "We deleted all images and left 5. Max limit!")
                                    return redirect(reverse('edit-rental', kwargs={'id': rental.id}))
                                else:
                                    messages.error(r, "You have reached your limit of 5 image uploads!")
                            else:
                                messages.error(r, f"{image} is not a valid image file. Should have: {good_extentions}")
                                return redirect(reverse('edit-rental', kwargs={'id': rental.id}))
                        rental.save()
                        messages.success(r, "Successfully added images")
                        return redirect(reverse('edit-rental', kwargs={'id': rental.id}))
            else:
                messages.error(r, "No pics or pic limit reached")
        messages.success(r, "Rental successfully editted!")
        return render(r, 'rentals/edit_rental.html', {'rental': rental, 'l_user': r.user.username})

    else:
        return render(r, 'rentals/edit_rental.html', {'rental': rental, 'l_user': r.user.username})


def availabe_rentals(r):
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

    return render(r, "rentals/availabe_rentals.html", {
        'rentals': rentals, 
        'search_query': search_query
    })


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

def rental_detail(r, id):
    rental = get_object_or_404(Rental, id=id)
    l_user = r.user.username
    likes = RentalRating.objects.filter(liked=True).count()
    dislikes = RentalRating.objects.filter(liked=False).count()
    user_rating = None
    if r.user.is_authenticated:
        user_rating = RentalRating.objects.filter(user=r.user, rental=rental).first()
    context = {
        'rental': rental,
        'l_user': l_user,
        'likes': likes,
        'dislikes': dislikes,
        'user_rating': user_rating
    }
    return render(r, 'themeforest/property-single.html', context=context)

@login_required(login_url='login')
def rented_rentals(r):
    rented = PaymentHistory.objects.filter(user=r.user)
    seen = set()
    u_rentals = []
    for u_rental in rented:
        if u_rental.rental.id not in seen:
            seen.add(u_rental.rental.id)
            u_rentals.append(u_rental)

    return render(r, 'rentals/rented.html', {'rentals': u_rentals})

def rooms(r):
    rooms = Rental.objects.filter(type_of_rental='room')
    return render(r, 'rentals/rooms.html', {'rentals': rooms})

def apartments(r):
    apartments = Rental.objects.filter(type_of_rental='apartment')
    return render(r, 'rentals/apartments.html', {'rentals': apartments})

def business_properties(r):
    business_properties = Rental.objects.filter(type_of_rental='business_property')
    return render(r, 'rentals/business_properties.html', {'rentals': business_properties})

def student_dorms(r):
    student_dorms = Rental.objects.filter(type_of_rental='student_dorm')
    return render(r, 'rentals/student_dorms.html', {'rentals': student_dorms})

@login_required
def toggle_rating(r, rental_id, action):
    if not r.user.is_authenticated:
        return JsonResponse({'error': 'You have to be logged in to rate a rental'}, status=403)
    
    rental = get_object_or_404(Rental, id=rental_id)

    try:
        rating = RentalRating.objects.get(user=r.user, rental=rental)
        if action == "undo":
            rating.delete()
        else:
            rating.liked = (action == "like")
            rating.save()
    except RentalRating.DoesNotExist:
        if action in ["like", "dislike"]:
            RentalRating.objects.create(
                user=r.user,
                rental=rental,
                liked=(action=="like")
            )
    counts = RentalRating.objects.filter(rental=rental).aggregate(
        likes=Count("id", filter=models.Q(liked=True)),
        dislikes=Count("id", filter=models.Q(liked=False))
    )
    return JsonResponse({
        'status': action,
        'likes': counts["likes"],
        'dislikes': counts["dislikes"]
    })


# @login_required
# def like_rental(r, id):
#     rental = get_object_or_404(Rental, id=id)
#     ratings = RentalRating.objects.filter(user=r.user)
#     if len(ratings) == 0:
#         new_rating = RentalRating.objects.create(user=r.user, rental=rental, liked=True)
#         new_rating.save()
#         return HttpResponse(200)
#     else:
#         ratings[0].delete()
#         return HttpResponse(200)


# @login_required
# def dislike_rental(r, id):
#     rental = get_object_or_404(Rental, id=id)
#     ratings = RentalRating.objects.filter(user=r.user)
#     if len(ratings) == 0:
#         new_rating = RentalRating.objects.create(user=r.user, rental=rental, liked=False)
#         new_rating.save()
#         return HttpResponse(200)
#     else:
#         ratings[0].delete()
#         return HttpResponse(200)

