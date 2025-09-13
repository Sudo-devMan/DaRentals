
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from datetime import datetime
from django.conf import settings
# from base.utils import create_subaccount
import requests
from django.core.mail import send_mail

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True)
    image = models.ImageField(upload_to='profiles', default='profiles/profile.png')
    address = models.TextField(default="South Africa")
    phone_number = models.CharField(max_length=50, default="No number")
    date_modified = models.DateTimeField(auto_now=True)
    # account_number = models.CharField(max_length=15, default="NONE")
    # bank_code = models.CharField(max_length=10, default="NONE")
    # subaccount_code = models.CharField(max_length=100, default='NONE')
    # subscription_code = models.CharField(max_length=100, default='NONE')
    # is_premium = models.BooleanField(default=False)
    # rent_spendings = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    # rent_earnings = models.DecimalField(max_digits=100, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} | Profile"

    # def save(self, *args, **kwargs):
    #     if (
    #         self.bank_code != "NONE" and
    #         self.account_number != "NONE" and
    #         self.subaccount_code == "NONE"
    #     ):
    #         subaccount = self.create_paystack_subaccount()
    #         if subaccount:
    #             self.subaccount_code = subaccount
    #             send_mail(
    #                 "DaRentals Account",
    #                 "Your bank account has been set up successfully. You can now receive rent money from tenants!",
    #                 "darentals@gmail.com",
    #                 [self.user.email],  # send_mail needs list
    #                 fail_silently=True
    #             )
    #     super().save(*args, **kwargs)

    # def create_paystack_subaccount(self):
    #     url = "https://api.paystack.co/subaccount"
    #     headers = {
    #         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    #         "Content-Type": "application/json",
    #     }
    #     data = {
    #         "business_name": self.user.username,
    #         "settlement_bank": self.bank_code,
    #         "account_number": self.account_number,
    #         "percentage_charge": 1.0,
    #     }

    #     response = requests.post(url, headers=headers, json=data)
    #     res_data = response.json()
    #     print("Paystack Response:", res_data)
    #     if res_data.get("status"):
    #         return res_data["data"].get("subaccount_code")
    #     return None

    # def delete_paystack_subaccount(self):
        url = f"https://api.paystack.co/subaccount/{self.subaccount_code}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
        }
        response = requests.delete(url, headers=headers)
        if response.status == 200:
            return True
        else:
            print("Failed to delete:", response.json())
            return False


def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        user_profile.follows.set([instance.profile.id])
        user_profile.save()

post_save.connect(create_profile, sender=User)


