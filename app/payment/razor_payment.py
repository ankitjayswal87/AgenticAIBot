import os
import razorpay
from constants import constant
from dotenv import load_dotenv
import logging
logger = logging.getLogger(__name__)

load_dotenv()

client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET")
    )
)

def create_payment_link(
    amount,
    description,
    name,
    contact,
    booking_id,
    email="",
    callback_url=constant.RAZORPAY_CALLBACK_URL
):
    """
    Create a Razorpay Payment Link.

    Args:
        amount (float|int): Amount in INR (e.g. 125 or 125.50)
        description (str): Payment description
        name (str): Customer name
        contact (str): Customer mobile number
        booking_id (str): Your internal booking ID
        email (str): Customer email (optional)
        callback_url (str): Redirect URL after payment

    Returns:
        dict: Razorpay payment link response
    """

    payment = client.payment_link.create({
        "amount": int(float(amount) * 100),   # Convert INR to paise
        "currency": "INR",
        "accept_partial": False,
        "description": description,
        "customer": {
            "name": name,
            "email": email,
            "contact": contact
        },
        "notify": {
            "sms": True,
            "email": True
        },
        "reminder_enable": True,
        "callback_url": callback_url,
        "callback_method": "get",
        "notes": {
            "booking_id": booking_id
        }
    })

    return payment