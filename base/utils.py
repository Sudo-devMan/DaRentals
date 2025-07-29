
from django.conf import settings
import requests
from django.http import HttpResponse
from django.utils import timezone
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from twilio.rest import Client

def send_sms(to, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to
        )
        return True
    except Exception as e:
        print("SMS error:", e)
        return False




def generate_receipt(payment):
    """
    Generates a PDF receipt for a PaymentHistory object.
    Saves it to media/receipts/ and updates the payment object.
    """
    # File path and directory
    filename = f"receipt_{payment.id}.pdf"
    folder_path = os.path.join(settings.MEDIA_ROOT, 'receipts')
    file_path = os.path.join(folder_path, filename)

    # Create receipts folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    # Set up the PDF
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, height - 80, "DaRentals Rent Receipt")

    # Details
    c.setFont("Helvetica", 12)
    line_height = 25
    y = height - 130

    details = [
        f"Payment Reference: {payment.reference}",
        f"User: {payment.user.username} ({payment.user.email})",
        f"Landlord: {payment.rental.user.username} | {payment.rental.user.profile.phone_number}",
        f"Rental Address: {payment.rental.address}",
        f"Amount Paid: R {payment.rental.price}",
        f"Date Paid: {payment.date.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Status: {'Successful' if payment.status else 'Failed'}",
    ]

    for line in details:
        c.drawString(50, y, line)
        y -= line_height

    # Footer
    c.drawString(50, y - 40, "Thank you for your payment!")
    c.drawString(50, y - 60, "This receipt serves as proof of transaction.")

    c.showPage()
    c.save()

    # Save receipt path in model
    payment.receipt.name = f"receipts/{filename}"
    payment.save()


# useless one this one. but do not touch hehe
def create_subaccount(business_name, account_number, bank_code):
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "business_name": business_name,
        "settlement_bank": bank_code,
        "account_number": account_number,
        "percentage_charge": 99.0,
        "description": "DaRentals landlord earnings",
    }

    response = requests.post("https://api.paystack.co/subaccount", headers=headers, json=data)
    
    if response.status_code == 200 and response.json().get("status"):
        return response.json()["data"]["subaccount_code"]
    
    print("Subaccount creation failed:", response.json())
    return "NONE"
