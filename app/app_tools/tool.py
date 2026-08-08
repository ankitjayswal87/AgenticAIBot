import time
import random
import json

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

embeddings = OpenAIEmbeddings()
vector_data = FAISS.load_local(constant.VECTOR_DB,embeddings,allow_dangerous_deserialization=True)

#verify the ticket details and confirm with user
@tool(return_direct=True)
def verify_confirm_ticket(from_city:str,to_city:str,journey_date:str,seats:str,runtime: ToolRuntime, config: RunnableConfig)->str:
    """Just verify all details received here"""
    print("JOURNEY_DATE:"+str(journey_date))
    #user_id = runtime.state["user_id"]
    user_id = config.get("configurable", {}).get("user_id")
    user_name = config.get("configurable", {}).get("user_name")
    print("USERNAME------------"+str(user_name))
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
    print("DATE OF EVENT:"+str(date_of_event))
    print("NUMBER OF PASSES:"+str(number_of_passes))
    print("TOTAL SILVER:"+str(total_silver_pass))
    print("TOTAL GOLD:"+str(total_gold_pass))
    print("TOTAL PLATINUM:"+str(total_platinum_pass))
    print("TOTAL COST:"+str(total_cost))
    user_id = config.get("configurable", {}).get("user_id")
    user_name = config.get("configurable", {}).get("user_name")
    print("USERNAME------------"+str(user_name))
    # store = runtime.store
    # store.put(("users",), user_id, {"booking_status":"confirmed_by_user"})
    
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
    

@tool
def send_payment_link(number_of_passes:str,date_of_event:str,total_silver_pass:str,total_gold_pass:str,total_platinum_pass:str,total_cost:str,runtime: ToolRuntime, config: RunnableConfig)->str:
    """Send payment link for event pass booking"""
    print("DATE OF EVENT:"+str(date_of_event))
    print("NUMBER OF PASSES:"+str(number_of_passes))
    print("TOTAL SILVER:"+str(total_silver_pass))
    print("TOTAL GOLD:"+str(total_gold_pass))
    print("TOTAL PLATINUM:"+str(total_platinum_pass))
    print("TOTAL COST:"+str(total_cost))
    #user_id = runtime.state["user_id"]
    user_id = config.get("configurable", {}).get("user_id")
    user_name = config.get("configurable", {}).get("user_name")
    phone = config.get("configurable", {}).get("phone")
    account_id = config.get("configurable", {}).get("account_id")
    booking_details = {"silver":total_silver_pass,"gold":total_gold_pass,"platinum":total_platinum_pass,"date_of_event":date_of_event}
    booking_details = json.dumps(booking_details)
    #user_info = runtime.store.get(("users",), user_id)
    #print("BOOKING STATUS:"+str(user_info))
    #BOOKING STATUS:Item(namespace=['users'], key='test123', value={'booking_status': 'confirmed_by_user'}, created_at='2026-04-28T09:40:13.222626+00:00', updated_at='2026-04-28T09:40:13.222629+00:00')
    #print("BOOKING STATUS:"+str(user_info.value['booking_status']))
    total_cost = "".join(c for c in total_cost if c.isdigit())
    amount=total_cost
    description="Event Ticket Booking"
    name=user_name
    contact=phone
    booking_id=generate_booking_id()
    #print(booking_id)
    payment = razor_payment.create_payment_link(amount,description,name,contact,booking_id)
    payment_id = payment["id"]
    payment_url = payment["short_url"]
    booking_db_id = pass_booking.insert_booking(account_id=account_id,phone=phone,connection=conn,booking_id=booking_id,payment_link_id=payment_id,amount=amount,status="pending",booking_details=booking_details)
    #return f"Your payment link for {total_silver_pass}-Silver {total_gold_pass}-Gold {total_platinum_pass}-Platinum, total {number_of_passes} pass tickets, of total value {total_cost} INR ,for the event date {date_of_event} is {payment_url} , Please click the payment link, to complete the payment and confirm your booking. Thank you!"
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