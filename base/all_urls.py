
from django.urls import path
from . import views
from rentals import views as rental_views
from auth_app import views as auth_views
from payments import views as payment_views

auth_urls = [
	path('sign-up', auth_views.sign_up, name='sign-up'),
    path('login', auth_views.login, name='login'),
    path('my-profile/<username>', auth_views.my_profile, name='my-profile'),
    path('edit-profile/<username>', auth_views.edit_profile, name='edit-profile'),
    path('logout', auth_views.log_out, name='logout'),
    path('u_sure_u_wanna_logout', auth_views.u_sure_u_wanna_logout, name='u_sure_u_wanna_logout'),
    path('u_sure_u_wanna_delete_your_account/<int:id>', auth_views.u_sure_u_wanna_delete_your_account, name='u_sure_u_wanna_delete_your_account'),
    path('delete-account/<int:id>', auth_views.delete_account, name='delete-account'),
    path('follow/<int:pk>', auth_views.follow, name='follow'),
    path('unfollow/<int:pk>', auth_views.unfollow, name='unfollow'),
    path('followers/<int:pk>', auth_views.followers, name='followers'),
]

rental_urls = [
	path('people-with-rooms', rental_views.landlords_page, name='people-with-rooms'),
    path('post-rental', rental_views.post_rental, name='post-rental'),
    path('rental/<int:id>', rental_views.rental_detail, name='rental'),
    path('edit-rental/<int:id>', rental_views.edit_rental, name='edit-rental'),
    path('u_sure_u_wanna_delete_your_rental/<int:id>', rental_views.u_sure_u_wanna_delete_your_rental, name='u_sure_u_wanna_delete_your_rental'),
    path('delete_rental/<int:id>', rental_views.delete_rental, name='delete_rental'),
    path('availabe-rentals', rental_views.availabe_rentals, name='availabe-rentals'),
    path('uyaphapha', rental_views.delete_rental, name='uyaphapha'),
    path('rented-rentals', rental_views.rented_rentals, name='rented-rentals'),
]

payment_urls = [
    path('', views.home, name='home'),
    path('failed/<int:id>', payment_views.payment_failed, name='failed'),
    path('success/<int:id>', payment_views.payment_successful, name='success'),
    path('checkout/<int:id>', payment_views.create_paystack_checkout_session, name='checkout'),
    path('webhook/paystack', payment_views.paystack_webhook), # go to paystack dashboard settings and paste "ngrokurl/mywebhookurl"
    path('my-payments', payment_views.my_payments, name='my-payments'),
    path('download/<payment_reference>', payment_views.download_receipt, name='download')
]


# https://f0fe6325c4ed.ngrok-free.app/webhook/paystack
# https://f0fe6325c4ed.ngrok-free.app