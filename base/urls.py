
from django.urls import path
from . import views
from . import all_urls
from rentals import views as rental_views
from auth_app import views as auth_views
from payments import views as payment_views


urlpatterns = [

    path('', views.landing, name='landing'),
    path('home', views.home, name='home-page'),
    path('search', views.search, name='search'),
    path('secret_656profiles', views.profiles, name='secret_656profiles'),
    path('secret_656profile/<int:id>', views.secret_profile, name='secret_656profile'),
    path('live-search/', views.live_search, name='live_search'),

     # extra space just in case (PS. why am I so lazy)

]

urlpatterns+=all_urls.auth_urls + all_urls.rental_urls + all_urls.payment_urls
