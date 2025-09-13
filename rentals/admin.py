
from django.contrib import admin
from .models import Rental, RentalImage, RentalRating

admin.site.register(Rental)
admin.site.register(RentalImage)
admin.site.register(RentalRating)
