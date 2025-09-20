from django.contrib.sitemaps import Sitemap
from .models import Rental

class RentalSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Rental.objects.all()  # all rentals

    def lastmod(self, obj):
        return obj.upload_date

    def location(self, obj):
        return f'/rental/{obj.id}/'  # your rental URLs
