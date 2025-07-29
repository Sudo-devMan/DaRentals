import json
import uuid
import hmac
import hashlib
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import PaymentHistory
from rentals.models import Rental
from .paystack import checkout
from base.utils import generate_receipt

from django.contrib.auth.models import User


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
        },
        "label": f"Rent payment for {rental.address}"
    }

    status, session_url_or_error = checkout(checkout_data)

    if status:
        return redirect(session_url_or_error)
    else:
        messages.error(request, session_url_or_error)
        return render(request, 'rentals/rental_detail.html', {'rental': rental})


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
                product_id = metadata.get("product_id")
                user_id = metadata.get("user_id")
                payment_id = metadata.get("payment_id")

                user = get_object_or_404(User, id=user_id)
                rental = get_object_or_404(Rental, id=int(product_id))
                rental.is_occupied = True
                rental.save()

                new_payment = PaymentHistory.objects.create(
                    user=user,
                    rental=rental,
                    reference=payment_id,
                    status=True,
                    date=datetime.now()
                )

                # dira receipt and call save
                generate_receipt(new_payment)

                # user_number = new_payment.user.profile.phone_number
                # landlord_number = rental.user.profile.phone_number

                # user_number = fix_number(user_number)
                # landlord_number = fix_number(landlord_number)

                # user_sms = f"DaRentals | Hi there! Your rent payment for '{rental.address} by {rental.user.username} | R{rental.price}' has reflected successfully! Check the receipt in your Profile page press view payments. Download the receipt and show the landlord."
                # landlord_sms = f"DaRentals | Hi there! {new_payment.user.username} ({new_payment.user.profile.phone_number}) has paid R{rental.price} rent for {rental.address}. Payments reference on the receipt we send to them is: {new_payment.reference}"

                # send_sms(user_number, user_sms)
                # send_sms(landlord_number, landlord_sms)

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
    receipt_path = payment.receipt.path
    response = FileResponse(open(receipt_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=receipt_for_{payment.rental.address}.pdf'
    return response
