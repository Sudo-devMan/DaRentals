
from django.db import models
from django.contrib.auth.models import User

class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='rentals', blank=False, null=False)
    address = models.CharField(max_length=300, blank=False, null=False)
    details = models.TextField(max_length=10000, blank=False, null=False)
    price  = models.DecimalField(decimal_places=2, max_digits=10, blank=False, null=False)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_occupied = models.BooleanField(default=False)

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.user.username} | {self.address}"
