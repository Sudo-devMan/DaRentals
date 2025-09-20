
from django.urls import path
from . import views
from . import all_urls
from rentals import views as rental_views
from auth_app import views as auth_views
from payments import views as payment_views
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from rentals.sitemaps import RentalSitemap

sitemaps = {
    'rentals': RentalSitemap,
}

urlpatterns = [

    path('', views.home, name='landing'),
    path('home', views.home, name='home-page'),
    path('home', views.home, name='home'),
    path('search', views.search, name='search'),
    path('secret_656profiles', views.profiles, name='secret_656profiles'),
    path('secret_656profile/<int:id>', views.secret_profile, name='secret_656profile'),
    path('live-search/', views.live_search, name='live_search'),
    path('terms-of-use', views.terms_of_use, name='terms-of-use'),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django-sitemap'),
     # extra space just in case

]

flufflesspatterns = [
    path('fluffhome', views.fluffhome, name='fluffhome')
]

urlpatterns+=all_urls.auth_urls + all_urls.rental_urls + all_urls.payment_urls + flufflesspatterns
