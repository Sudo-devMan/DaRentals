
from django.db import models
from django.contrib.auth.models import User
from rentals.models import Rental
from django.utils import timezone
from datetime import timedelta

class PaymentHistory(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	status = models.BooleanField(default=False)
	receipt =models.FileField(null=True, blank=True, upload_to='receipts')
	reference = models.CharField()

	def __str__(self):
		return f"{self.user.username} Paid for {self.rental.address}"

class Subscription(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	plan_name = models.CharField(max_length=50)
	paystack_subscription_id = models.CharField(max_length=100)
	active = models.BooleanField(default=False)
	start_date = models.DateTimeField(default=timezone.now)
	end_date = models.DateTimeField(null=True, blank=True)

	def save(self, *args, **kwargs):
		if not self.end_date:
			self.end_date = self.start_date + timedelta(days=30)
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.user.username} | {self.plan_name}"
