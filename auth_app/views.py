
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rentals.models import Rental
from datetime import datetime
from base.utils import update_paystack_subbaccount

@login_required(login_url='login')
def my_profile(r, username):
    l_user = User.objects.get(username=username)
    rentals = Rental.objects.filter(user=l_user)
    profile = get_object_or_404(Profile, user=l_user)
    logged_in_user = r.user.username
    wegood = False
    if logged_in_user == profile.user.username:
        wegood = True

    if r.method == 'POST':
        current_user_profile = r.user.profile
        action = r.POST.get('follow')

        if action == 'unfollow':
            current_user_profile.follows.remove(profile)
        elif action == 'follow':
            current_user_profile.follows.add(profile)
        current_user_profile.save()
    context = {
        'rentals': rentals,
        'l_user': l_user,
        'logged_in_user': logged_in_user,
        'profile': profile,
        'wegood': wegood
    }
    return render(r, 'auth/my-profile.html', context)

# FIX PROFILE PICTURE EDITING [DONE. Problem: I did not properly configure the edit form to accept files]
@login_required(login_url='login')
def edit_profile(r, username):
    l_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=l_user)
    wegood = False
    # old_acc = profile.account_number
    # old_bank = profile.bank_code

    if r.user.username == l_user.username:
        wegood = True
    else:
        wegood = False

    if r.method == 'POST':
        new_username = r.POST.get('username')
        address = r.POST.get('address')
        phone_number = r.POST.get('phone_number')
        l_user.username = new_username
        l_user.save()
        profile.address = address
        profile.phone_number = phone_number
        if r.FILES.get('profile_image') != None:
            profile.image.delete()
            profile.image = r.FILES.get('profile_image')
        profile.date_modified = datetime.now()
        # profile.account_number = r.POST.get('account_number')
        # profile.bank_code = r.POST.get('bank_code')

        # if profile.subaccount_code != "NONE":
        #     if old_acc != profile.account_number or old_bank != profile.bank_code:
        #         subaccount_code = update_paystack_subbaccount(profile.subaccount_code, profile.bank_code, profile.account_number)
        #         if subaccount_code:
        #             profile.account_number = r.POST.get('account_number')
        #             profile.bank_code = r.POST.get('bank_code')
        #             profile.subaccount_code = subaccount_code
        #             messages.info(r, "Successfully updated bank details")
        #         else:
        #             messages.info(r, "Failed to update bank details. Try again.")

        profile.save()
        messages.success(r, f'Changes saved! ({datetime.now()})')
        return render(r, 'auth/edit-my-profile.html', {
            'l_user': l_user,
            'profile': profile,
            'wegood': wegood,
        })

    return render(r, 'auth/edit-my-profile.html', {
        'l_user': l_user,
        'profile': profile,
        'wegood': wegood,
    })

def why_not_to_unfollow_myself(r):
    return render(r, 'auth/why_not_to_unfollow_myself.html')

def sign_up(r):
    if r.method == 'POST':
        username = r.POST.get('username')
        email = r.POST.get('email')
        password1 = r.POST.get('password1')
        password2 = r.POST.get('password2')

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(r, "Someone else took that name! Try another")
                return redirect('sign-up')
            elif User.objects.filter(email=email).exists():
                messages.info(r, "Someone else is using that email! Try another")
                return redirect('sign-up')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save();
                login_user = authenticate(username=username, email=email, password=password1)
                auth.login(r, login_user)

                return redirect('edit-profile/' + username)
        else:
            messages.info(r, "Bruh.. them passwords don\'t match!")
            return redirect('sign-up')
    else:
        return render(r, 'auth/sign-up.html')

def login(r):
    if r.method == 'POST':
        username = r.POST.get('username')
        password = r.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.info(r, "Username incorrect or you don't have an account")
            return redirect('login')

        login_user = authenticate(username=username, password=password)

        if login_user is not None:
            auth.login(r, login_user)
            return redirect('home-page')
        else:
            messages.info(r, "Incorrect password!!")
            return redirect('login')
    else:
        return render(r, 'auth/login.html')

@login_required(login_url='login')
def u_sure_u_wanna_logout(r):
    return render(r, 'auth/u_sure_u_wanna_logout.html')

@login_required(login_url='login')
def u_sure_u_wanna_delete_your_account(r, id):
    the_user = User.objects.get(id=id)
    return render(r, 'auth/u_sure_u_wanna_delete_your_account.html', {'the_user': the_user})

@login_required(login_url='login')
def delete_account(r, id):
    user = User.objects.get(id=id)
    profile = Profile.objects.get(user=user)

    if r.user.username == user.username and r.user.username == profile.user.username:
        user.delete()
        return redirect('/')
    else:
        return render(r, 'public/uyaphapha.html')

@login_required(login_url='login')
def log_out(r):
    logout(r)
    return redirect('/')

@login_required(login_url='login')
def followers(r, pk):
    the_user = r.user
    if r.method == 'POST':
        current_user_profile = r.user.profile
        action = r.POST.get('follow')

        if action == 'unfollow':
            current_user_profile.follows.remove(profile)
        elif action == 'follow':
            current_user_profile.follows.add(profile)
        current_user_profile.save()
    if r.user.id == pk:
        followers_all = Profile.objects.get(user_id=pk).followed_by.all()
        return render(r, 'auth/followers.html', {'followers': followers_all, 'the_user': the_user})
    else:
        return render(r, 'public/uyaphapha.html')

@login_required(login_url='login')
def follow(r, pk):
    profile = get_object_or_404(Profile, id=pk)
    l_user = r.user.profile

    if l_user in profile.follows.all():
        return redirect(r.META.get("HTTP_REFERER"))
    else:
        l_user.follows.add(profile)
        l_user.save()
        return redirect(r.META.get("HTTP_REFERER"))

@login_required(login_url='login')
def unfollow(r, pk):
    # get, remove, save
    profile = get_object_or_404(Profile, id=pk)
    l_user = r.user.profile

    if l_user in profile.follows.all():
        l_user.follows.remove(profile)
        l_user.save()
        return redirect(r.META.get("HTTP_REFERER"))
    else:
        return redirect(r.META.get("HTTP_REFERER"))
