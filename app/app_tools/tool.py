from langchain.tools import tool, ToolRuntime
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnableConfig

from constants import constant

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