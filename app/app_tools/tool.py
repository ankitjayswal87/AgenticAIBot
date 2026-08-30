import time
import random
import json
from datetime import datetime, date, timedelta
import logging
logger = logging.getLogger(__name__)

import mysql.connector
conn = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="8FRf4T",
    database="event_booking"
)
from db_operations import pass_booking

from langchain.tools import tool, ToolRuntime
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnableConfig

from constants import constant
from payment import razor_payment

def generate_booking_id():
    timestamp = int(time.time())  # Unix timestamp
    rand = random.randint(1000, 9999)
    return f"TKT{timestamp}{rand}"

def generate_appointment_id():
    timestamp = int(time.time())  # Unix timestamp
    rand = random.randint(1000, 9999)
    return f"APT{timestamp}{rand}"

embeddings = OpenAIEmbeddings()
vector_data = FAISS.load_local(constant.VECTOR_DB,embeddings,allow_dangerous_deserialization=True)

#verify the ticket details and confirm with user
@tool(return_direct=True)
def verify_confirm_ticket(from_city:str,to_city:str,journey_date:str,seats:str,runtime: ToolRuntime, config: RunnableConfig)->str:
    """Just verify all details received here"""
    print(f"JOURNEY_DATE: {journey_date}")
    #user_id = runtime.state["user_id"]
    user_id = config.get("configurable", {}).get("user_id")
    user_name = config.get("configurable", {}).get("user_name")
    print(f"USERNAME: {user_name}")
    store = runtime.store
    store.put(("users",), user_id, {"booking_status":"confirmed_by_user"})
    
    if user_id=="test123":
        return f"Okay, Prahi you are going to book total {seats} tickets from {from_city} to {to_city} on date {journey_date}, Please confirm to book it!"
    else:
        return f"Okay, you are going to book total {seats} tickets from {from_city} to {to_city} on date {journey_date}, Please confirm to book it!"

#ticket booking function
@tool(return_direct=True)
def book_bus_ticket(from_city:str,to_city:str,journey_date:str,seats:str,runtime: ToolRuntime, config: RunnableConfig)->str:
    """Book bus ticket between given two cities"""
    print("JOURNEY_DATE:"+str(journey_date))
    print("FROM CITY:"+str(from_city))
    print("TO CITY:"+str(to_city))
    print("SEATS:"+str(seats))
    #user_id = runtime.state["user_id"]
    user_id = config.get("configurable", {}).get("user_id")
    user_info = runtime.store.get(("users",), user_id)
    #print("BOOKING STATUS:"+str(user_info))
    #BOOKING STATUS:Item(namespace=['users'], key='test123', value={'booking_status': 'confirmed_by_user'}, created_at='2026-04-28T09:40:13.222626+00:00', updated_at='2026-04-28T09:40:13.222629+00:00')
    print("BOOKING STATUS:"+str(user_info.value['booking_status']))
    return f"Your {seats} tickets from {from_city} to {to_city} on {journey_date} have been reserved. Please click the payment link sent to your mobile number, to complete the payment and confirm your booking. Thank you!"

#search query here for general FAQs
@tool
def knowledge_base(query:str)->str:
    """Search here for general questions regarding bus policy"""
    docs = vector_data.similarity_search(query,k=2)
    return docs


@tool(return_direct=True)
def verify_confirm_pass_ticket(number_of_passes:str,date_of_event:str,total_silver_pass:str,total_gold_pass:str,total_platinum_pass:str,total_cost:str,runtime: ToolRuntime, config: RunnableConfig)->str:
    """Just verify all details received here"""
    # print(f"DATE OF EVENT: {date_of_event}")
    # print(f"NUMBER OF PASSES: {number_of_passes}")
    # print(f"TOTAL SILVER: {total_silver_pass}")
    # print(f"TOTAL GOLD: {total_gold_pass}")
    # print(f"TOTAL PLATINUM: {total_platinum_pass}")
    # print(f"TOTAL COST: {total_cost}")
    logger.info("DATE OF EVENT: %s", date_of_event)
    logger.info("NUMBER OF PASSES: %s", number_of_passes)
    logger.info("TOTAL SILVER: %s", total_silver_pass)
    logger.info("TOTAL GOLD: %s", total_gold_pass)
    logger.info("TOTAL PLATINUM: %s", total_platinum_pass)
    logger.info("TOTAL COST: %s", total_cost)
    user_id = config.get("configurable", {}).get("user_id")
    user_name = config.get("configurable", {}).get("user_name")
    #print(f"USERNAME: {user_name}")
    logger.info("USERNAME: %s", user_name)
    
    if user_id=="test123":
        #return f"Okay, Prahi you are going to book {total_silver_pass}-Silver {total_gold_pass}-Gold {total_platinum_pass}-Platinum, total {number_of_passes} pass tickets of total value {total_cost}, for the date {date_of_event}, Please confirm to get payment link!"
        return f"""🎟️ *Booking Confirmation*

        Okay, Prahi 😊

        You are going to book:

        🥈 *Silver:* {total_silver_pass} pass(es)
        🥇 *Gold:* {total_gold_pass} pass(es)
        💎 *Platinum:* {total_platinum_pass} pass(es)

        🎫 *Total Passes:* {number_of_passes}
        💰 *Total Amount:* ₹{total_cost}
        📅 *Event Date:* {date_of_event}

        Please *confirm your booking* to receive the 💳 *Payment Link*.
        """
    else:
        #return f"Okay, you are going to book {total_silver_pass}-Silver {total_gold_pass}-Gold {total_platinum_pass}-Platinum, total {number_of_passes} pass tickets of total value {total_cost}, for the date {date_of_event} Please confirm to get payment link!"
        return f"""🎟️ *Booking Confirmation*
        
        Okay, You are going to book:
        
        🥈 *Silver:* {total_silver_pass} pass(es)
        🥇 *Gold:* {total_gold_pass} pass(es)
        💎 *Platinum:* {total_platinum_pass} pass(es)
        
        🎫 *Total Passes:* {number_of_passes}
        💰 *Total Amount:* ₹{total_cost}
        📅 *Event Date:* {date_of_event}
        
        Please *confirm your booking* to receive the 💳 *Payment Link*.
        """
    
@tool(return_direct=True)
def verify_confirm_appointment(
    appointment_date: str,
    appointment_time: str,
    runtime: ToolRuntime,
    config: RunnableConfig
) -> str:
    """Verify the appointment date and time before confirming the booking."""

    logger.info("APPOINTMENT DATE: %s", appointment_date)
    logger.info("APPOINTMENT TIME: %s", appointment_time)

    user_id = config.get("configurable", {}).get("user_id")
    user_name = config.get("configurable", {}).get("user_name")

    logger.info("USERNAME: %s", user_name)

    # Get current date
    today = date.today()
    current_year = today.year

    try:
        # Convert received date from dd-mm-yyyy
        appointment_dt = datetime.strptime(
            appointment_date,
            "%d-%m-%Y"
        ).date()

        # Always use current year
        if appointment_dt.year != current_year:
            appointment_dt = appointment_dt.replace(year=current_year)

        # Rewrite date in required format
        appointment_date = appointment_dt.strftime("%d-%m-%Y")
        store = runtime.store
        store.put(("users",), user_id, {"appointment_date":appointment_date})

        logger.info("UPDATED APPOINTMENT DATE: %s", appointment_date)

    except ValueError:
        return """❌ Invalid appointment date.

        Please provide the appointment date in this format:
        📅 *dd-mm-yyyy*

        Example: *28-08-2026*
        """

    # Allowed booking range:
    # Today -> 3 days from today
    max_date = today + timedelta(days=constant.ADVANCE_BOOKING_DAYS)

    # Check if appointment date is valid
    if appointment_dt < today:
        logger.warning("APPOINTMENT CANNOT BE BOOKED FOR A PAST DATE: %s",appointment_dt)
        return f"""❌ Sorry, appointments cannot be booked for a past date.

        📅 Please choose a date between *{today.strftime("%d-%m-%Y")}* and *{max_date.strftime("%d-%m-%Y") }*.
        """

    if appointment_dt > max_date:
        logger.warning("APPOINTMENT CAN BE BOOKED WITHIN NEXT 3 DAYS ONLY: %s",appointment_dt)
        return f"""❌ Sorry, appointments can only be booked within the next 3 days.

        📅 Please choose a date between *{today.strftime("%d-%m-%Y")}* and *{max_date.strftime("%d-%m-%Y")}*.
        """
        
    appointment_count = pass_booking.get_appointment_count(connection=conn,appointment_date=appointment_date,appointment_time=appointment_time)
    if appointment_count>=constant.MAX_BOOKINGS_PER_SLOT:
        logger.warning("SELECTED TIME SLOT IS FULL: %s",appointment_time)
        return f"""❌ Sorry, the selected slot {appointment_time} is full, Please choose another slot.
        """

    if user_id == "test123":
        customer_name = "Prahi"
    else:
        customer_name = user_name or "there"

    return f"""💇‍♀️ *Appointment Confirmation*

    Hello {customer_name} 😊

    Here are your appointment details:

    📅 *Date:* {appointment_date}
    ⏰ *Time:* {appointment_time}

    Please *confirm your appointment* to proceed. ✅
    """

@tool
def send_payment_link(number_of_passes:str,date_of_event:str,total_silver_pass:str,total_gold_pass:str,total_platinum_pass:str,total_cost:str,runtime: ToolRuntime, config: RunnableConfig)->str:
    """Send payment link for event pass booking"""
    
    # print(f"DATE OF EVENT: {date_of_event}")
    # print(f"NUMBER OF PASSES: {number_of_passes}")
    # print(f"TOTAL SILVER: {total_silver_pass}")
    # print(f"TOTAL GOLD: {total_gold_pass}")
    # print(f"TOTAL PLATINUM: {total_platinum_pass}")
    # print(f"TOTAL COST: {total_cost}")
    logger.info("DATE OF EVENT: %s", date_of_event)
    logger.info("NUMBER OF PASSES: %s", number_of_passes)
    logger.info("TOTAL SILVER: %s", total_silver_pass)
    logger.info("TOTAL GOLD: %s", total_gold_pass)
    logger.info("TOTAL PLATINUM: %s", total_platinum_pass)
    logger.info("TOTAL COST: %s", total_cost)   
    #user_id = runtime.state["user_id"]
    user_id = config.get("configurable", {}).get("user_id")
    user_name = config.get("configurable", {}).get("user_name")
    phone = config.get("configurable", {}).get("phone")
    account_id = config.get("configurable", {}).get("account_id")
    booking_details = {"silver":total_silver_pass,"gold":total_gold_pass,"platinum":total_platinum_pass,"date_of_event":date_of_event}
    booking_details = json.dumps(booking_details)
    #user_info = runtime.store.get(("users",), user_id)
    #BOOKING STATUS:Item(namespace=['users'], key='test123', value={'booking_status': 'confirmed_by_user'}, created_at='2026-04-28T09:40:13.222626+00:00', updated_at='2026-04-28T09:40:13.222629+00:00')
    #print("BOOKING STATUS:"+str(user_info.value['booking_status']))
    total_cost = "".join(c for c in total_cost if c.isdigit())
    amount=total_cost
    description="Event Ticket Booking"
    name=user_name
    contact=phone
    booking_id=generate_booking_id()
    if booking_id:
        logger.info("UNIQUE BOOKING ID GENERATED TO INSERT: %s", booking_id)
    payment = razor_payment.create_payment_link(amount,description,name,contact,booking_id)
    if payment:
        payment_id = payment["id"]
        payment_url = payment["short_url"]
        logger.info("PAYMENT LINK CREATED: %s", payment_url)
        booking_db_id = pass_booking.insert_booking(account_id=account_id,phone=phone,connection=conn,booking_id=booking_id,payment_link_id=payment_id,amount=amount,status="pending",booking_details=booking_details)
        return f"""💳 *Payment Link for Your Booking*

        🎟️ *Pass Details:*

        🥈 Silver: {total_silver_pass} pass(es)
        🥇 Gold: {total_gold_pass} pass(es)
        💎 Platinum: {total_platinum_pass} pass(es)

        🎫 **Total Passes:** {number_of_passes}
        💰 **Total Amount:** ₹{total_cost}
        📅 **Event Date:** {date_of_event}

        🔗 *Payment Link:* {payment_url}

        👉 Please click the payment link above to complete your payment and *confirm your booking*. ✅

        🙏 Thank you for choosing *Dandiya Mahotsav 2026!* 🎉💃🕺
        """
    else:
        logger.warning("FAIL TO CREATE PAYMENT LINK")
        return f"""Something went wrong while creating your Payment link, Please Try Again"""

@tool(return_direct=True)
def book_appointment(
    appointment_date: str,
    appointment_time: str,
    runtime: ToolRuntime,
    config: RunnableConfig
) -> str:
    """Book a salon appointment and save the booking details in the database."""

    user_id = config.get("configurable", {}).get("user_id")
    user_name = config.get("configurable", {}).get("user_name")
    phone = config.get("configurable", {}).get("phone")
    account_id = config.get("configurable", {}).get("account_id")
    
    user_info = runtime.store.get(("users",), user_id)
    appointment_date = user_info.value['appointment_date']
    
    # print("APPOINTMENT DATE: " + str(appointment_date))
    # print("APPOINTMENT TIME: " + str(appointment_time))

    # print("USER ID: " + str(user_id))
    # print("USERNAME: " + str(user_name))
    # print("PHONE: " + str(phone))
    # print("ACCOUNT ID: " + str(account_id))
    
    logger.info("APPOINTMENT DATE: %s", appointment_date)
    logger.info("APPOINTMENT TIME: %s", appointment_time)
    logger.info("USER ID: %s", user_id)
    logger.info("USERNAME: %s", user_name)
    logger.info("PHONE: %s", phone)
    logger.info("ACCOUNT ID: %s", account_id)

    # Prepare appointment details
    booking_details = {
        "appointment_date": appointment_date,
        "appointment_time": appointment_time
    }

    booking_details = json.dumps(booking_details)

    # Generate unique booking ID
    appointment_id = generate_appointment_id()
    if appointment_id:
        logger.info("APPOINTMENT ID CREATED TO INSERT: %s", appointment_id)

    # Insert appointment into salon_bookings table
    booking_db_id = pass_booking.insert_salon_booking(
        account_id=account_id,
        phone=phone,
        connection=conn,
        booking_id=appointment_id,
        status="CONFIRMED",
        booking_details=booking_details
    )

    logger.info("SALON BOOKING DB ID: %s", booking_db_id)

    return f"""💇‍♀️ *Appointment Confirmed!* 🎉

    Hello {user_name or "there"} 😊

    Your salon appointment has been successfully booked.

    📅 *Date:* {appointment_date}
    ⏰ *Time:* {appointment_time}

    🎫 *Booking ID:* {appointment_id}

    ✅ *Status:* Confirmed

    🙏 Thank you for choosing *Ethereal Salon!* 💇‍♀️✨
    """