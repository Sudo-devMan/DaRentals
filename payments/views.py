import json
import uuid
import hmac
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import PaymentHistory, Subscription
from rentals.models import Rental
from .paystack import checkout
from base.utils import generate_receipt

import os
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone


def fix_number(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    if phone.startswith("+27") and len(phone) == 12:
        return phone
    elif phone.startswith("0") and len(phone) == 10:
        return "+27" + phone[1:]
    elif phone.startswith("27") and len(phone) == 11:
        return "+" + phone
    else:
        return None 


@login_required(login_url='login')
def payment_successful(request, id):
    rental = get_object_or_404(Rental, id=id)
    return render(request, 'payments/success.html', {'rental': rental})


@login_required(login_url='login')
def payment_failed(request, id):
    rental = get_object_or_404(Rental, id=id)
    return render(request, 'payments/error.html', {'rental': rental})


@login_required(login_url='login')
def create_paystack_checkout_session(request, id):
    rental = get_object_or_404(Rental, id=id)
    payment_id = f"payment_{uuid.uuid4()}"

    success_url = reverse('success', kwargs={'id': id})
    callback_url = f"{request.scheme}://{request.get_host()}{success_url}"

    checkout_data = {
        "email": request.user.email,
        "subaccount": rental.user.profile.subaccount_code,
        "amount": int(float(rental.price) * 100),
        "currency": "ZAR",
        "channels": ["card", "bank_transfer", "bank", "ussd", "qr", "mobile_money"],
        "reference": payment_id,
        "callback_url": callback_url,
        "metadata": {
            "product_id": id,
            "user_id": request.user.id,
            "payment_id": payment_id,
            "type": "rental",
        },
        "label": f"Rent payment for {rental.address}"
    }

    status, session_url_or_error = checkout(checkout_data)

    if status:
        return redirect(session_url_or_error)
    else:
        messages.error(request, session_url_or_error)
        print("Eyy, Mokhatxwa. Look:")
        print(session_url_or_error)
        return render(request, 'themeforest/property-single.html', {'rental': rental})


@csrf_exempt
def paystack_webhook(request):
    secret = settings.PAYSTACK_SECRET_KEY
    request_body = request.body
    print("Webhook callleeeedd!!")

    hash_ = hmac.new(secret.encode('utf-8'), request_body, hashlib.sha512).hexdigest()

    if hash_ == request.META.get('HTTP_X_PAYSTACK_SIGNATURE'):
        try:
            webhook_data = json.loads(request_body)
            print(webhook_data)

            if webhook_data["event"] == "charge.success":
                metadata = webhook_data["data"]["metadata"]
                user_id = metadata.get("user_id")
                payment_id = metadata.get("payment_id")
                user = get_object_or_404(User, id=user_id)

                if metadata.get("type") == "subscription":
                    # ✅ Subscription payment
                    user.profile.is_premium = True
                    user.profile.save()

                    Subscription.objects.update_or_create(
                        user=user,
                        defaults={
                            "plan_name": "Premium",
                            "paystack_subscription_id": webhook_data["data"]["reference"],
                            "active": True,
                            "start_date": timezone.now(),
                            "end_date": timezone.now() + timedelta(days=30),
                        },
                    )
                    print(f"✅ Subscription activated for {user.username}")

                else:
                    # ✅ Rental payment
                    product_id = metadata.get("product_id")
                    rental = get_object_or_404(Rental, id=int(product_id))
                    rental.is_occupied = True
                    rental.money_made += Decimal(str(rental.price))
                    rental.save()

                    new_payment = PaymentHistory.objects.create(
                        user=user,
                        rental=rental,
                        reference=payment_id,
                        status=True,
                        date=datetime.now()
                    )
                    new_payment.save()
                    new_payment.user.profile.rent_spendings += Decimal(str(rental.price))
                    new_payment.user.profile.save()
                    rental.user.profile.rent_earnings += Decimal(str(rental.price))
                    rental.user.profile.save()

                    generate_receipt(new_payment)
                    print('Receipt generated')

        except Exception as e:
            print("Webhook error:", e)

    return HttpResponse("OK", status=200)


@login_required(login_url='login')
def my_payments(request):
    payments = PaymentHistory.objects.filter(user=request.user)
    return render(request, "payments/my_payments.html", {'payments': payments})


@login_required(login_url='login')
def download_receipt(request, payment_reference):
    payment = get_object_or_404(PaymentHistory, reference=payment_reference)
    
    if not payment.receipt:
        raise Http404("Receipt not found.")

    receipt_path = payment.receipt.path

    if not os.path.exists(receipt_path):
        raise Http404("Receipt file does not exist.")

    filename = f"DaRentals_receipt_for_{slugify(payment.rental.address)}.pdf"

    response = FileResponse(open(receipt_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ---------------- PREMIUM SUBSCRIPTIONS ---------------- #

@login_required(login_url='login')
def subscribe(request):
    """Start a Paystack checkout for premium subscription"""
    payment_id = f"sub_{uuid.uuid4()}"

    success_url = reverse('subscription_page')
    callback_url = f"{request.scheme}://{request.get_host()}{success_url}"

    checkout_data = {
        "email": request.user.email,
        "amount": 5000 * 100,  # e.g. R50.00 → adjust as needed
        "currency": "ZAR",
        "channels": ["card", "bank_transfer", "ussd", "qr", "mobile_money"],
        "reference": payment_id,
        "callback_url": callback_url,
        "metadata": {
            "user_id": request.user.id,
            "payment_id": payment_id,
            "type": "subscription",
        },
        "label": f"Premium Subscription for {request.user.username}"
    }

    status, session_url_or_error = checkout(checkout_data)

    if status:
        return redirect(session_url_or_error)
    else:
        messages.error(request, session_url_or_error)
        return redirect("home")


@login_required(login_url='login')
def subscription_page(request):
    """Simple landing page after subscription attempt"""
    return render(request, "payments/subscribe.html")
