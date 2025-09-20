
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from base.storage_backends import SupabaseStorage

supabase_storage = SupabaseStorage()

class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=300, blank=False, null=False)
    details = models.TextField(max_length=10000, blank=False, null=False)
    price  = models.DecimalField(decimal_places=2, max_digits=10, blank=False, null=False)
    money_made = models.DecimalField(decimal_places=2, max_digits=10, default=0.0)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_occupied = models.BooleanField(default=False)
    size = models.CharField(default='Size not specified')
    beds = models.IntegerField(default=0)
    baths = models.IntegerField(default=0)
    is_popular = models.BooleanField(default=False)
    type_of_rental = models.CharField(default='room')

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.user.username} | {self.address}"

class RentalImage(models.Model):
    image = models.ImageField(storage=supabase_storage, upload_to='rentals', null=False, blank=False)
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name="images", null=True)

    def __str__(self):
        return f"Rental Image | {self.rental.user.username} | {self.rental.address}"

    class Meta:
        ordering = ['-rental']

class RentalTenants(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='tenants')
    first_rent_payment = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    moved_in_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tenant for {self.rental.address}"

class RentalRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_date = models.DateTimeField(auto_now=True)
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='likes')
    liked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-liked_date']
        unique_together = ('user', 'rental')
    
    def __str__(self):
        return f"Rental Like | {self.user.username} | {self.rental.address}"
