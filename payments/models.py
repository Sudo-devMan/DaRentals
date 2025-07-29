
from django.db import models
from django.contrib.auth.models import User
from rentals.models import Rental

class PaymentHistory(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	status = models.BooleanField(default=False)
	receipt =models.FileField(null=True, blank=True, upload_to='receipts')
	reference = models.CharField()

	def __str__(self):
		return f"{self.user.username} Paid for {self.rental.address}"
