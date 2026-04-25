from langchain.tools import tool, ToolRuntime

#verify the ticket details and confirm with user
@tool(return_direct=True)
def verify_confirm_ticket(from_city:str,to_city:str,journey_date:str,seats:str,runtime: ToolRuntime)->str:
    """Just verify all details received here"""
    print("JOURNEY_DATE:"+str(journey_date))
    user_id = runtime.state["user_id"]
    print("BOOKING STATUS:"+str(runtime.state["booking_status"]))
    if user_id=="test123":
        return f"Okay, Ankit you are going to book total {seats} tickets from {from_city} to {to_city} on date {journey_date}, Please confirm to book it!"
    else:
        return f"Okay, you are going to book total {seats} tickets from {from_city} to {to_city} on date {journey_date}, Please confirm to book it!"

#ticket booking function
@tool(return_direct=True)
def book_bus_ticket(from_city:str,to_city:str,journey_date:str,seats:str)->str:
    """Book bus ticket between given two cities"""
    print("JOURNEY_DATE:"+str(journey_date))
    print("FROM CITY:"+str(from_city))
    print("TO CITY:"+str(to_city))
    print("SEATS:"+str(seats))
    #return f"Your {seats} tickets are booked from {from_city} to {to_city} on date {journey_date} ,, the payment link has been sent to your mobile number, just click on it to pay to confirm tickets, Thank you!"
    return f"Your {seats} tickets from {from_city} to {to_city} on {journey_date} have been reserved. Please click the payment link sent to your mobile number, to complete the payment and confirm your booking. Thank you!"