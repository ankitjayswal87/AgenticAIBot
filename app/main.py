import os
import json
import qrcode
from dotenv import load_dotenv
load_dotenv()

#langchain imports
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import dynamic_prompt, ModelRequest, before_model, after_model, SummarizationMiddleware
from langgraph.store.memory import InMemoryStore

#flask imports
from flask import Flask, jsonify, request, send_file, redirect,has_request_context,make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

#internal imports
from constants import constant
from app_tools import tool
from prompts import prompt
from agent_states import agent_state
from agent_contexts import agent_context
from hooks import hook
from whatsapp import send_message
from db_operations import pass_booking

import mysql.connector
conn = mysql.connector.connect(
    host=constant.MYSQL_DB_HOST,
    user=constant.MYSQL_DB_USER,
    password=constant.MYSQL_DB_PASS,
    database=constant.MYSQL_DB
)

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")

def generate_booking_qr(booking_id):
    qr_data = {"booking_id": booking_id}
    qr = qrcode.make(json.dumps(qr_data))
    filename = f"qr_{booking_id}.png"
    filename_save = f"/var/www/html/QRCodes/qr_{booking_id}.png"
    qr.save(filename_save)
    return filename

app = Flask(__name__)
limiter = Limiter(get_remote_address,app=app,default_limits=["1000 per day", "100 per hour"])

#get your agent state_schema here
state_schema = agent_state.CustomState

#get your agent context_schema here
context_schema = agent_context.Context

#get your system prompt for app
system_prompt=prompt.system_prompt

#get your dynamic system prompt here
dynamic_system_prompt = prompt.dynamic_system_prompt
dynamic_system_prompt_pass_booking = prompt.dynamic_system_prompt_pass_booking
dynamic_system_prompt_salon_appointment_booking = prompt.dynamic_system_prompt_appointment_booking

#get your hooks here
log_before_model = hook.log_before_model
log_after_model = hook.log_after_model

#get your tools for app
tools = [tool.verify_confirm_ticket,tool.book_bus_ticket,tool.knowledge_base]
tools_pass_booking = [tool.verify_confirm_pass_ticket,tool.send_payment_link]
tools_salon_appointment_booking = [tool.verify_confirm_appointment,tool.book_appointment]

store = InMemoryStore()

#create your agent here
agent = create_agent(
    model=constant.MODEL,
    tools=tools,
    store=store,
    #system_prompt=system_prompt,
    checkpointer=InMemorySaver(),
    #state_schema=state_schema,
    context_schema=context_schema,
    middleware=[
        dynamic_system_prompt,
        log_before_model,
        log_after_model,
        SummarizationMiddleware(
            model=constant.MODEL,
            trigger=("messages",constant.TRIGGER_MESSAGE_COUNT),
            keep=("messages",constant.KEEP_MESSAGE_COUNT)
        )
    ]
    )

agent_pass_booking = create_agent(
    model=constant.MODEL,
    tools=tools_pass_booking,
    store=store,
    #system_prompt=system_prompt,
    checkpointer=InMemorySaver(),
    #state_schema=state_schema,
    context_schema=context_schema,
    middleware=[
        dynamic_system_prompt_pass_booking,
        log_before_model,
        log_after_model,
        SummarizationMiddleware(
            model=constant.MODEL,
            trigger=("messages",constant.TRIGGER_MESSAGE_COUNT),
            keep=("messages",constant.KEEP_MESSAGE_COUNT)
        )
    ]
    )

agent_salon_appointment_booking = create_agent(
    model=constant.MODEL,
    tools=tools_salon_appointment_booking,
    store=store,
    checkpointer=InMemorySaver(),
    context_schema=context_schema,
    middleware=[
        dynamic_system_prompt_salon_appointment_booking,
        log_before_model,
        log_after_model,
        SummarizationMiddleware(
            model=constant.MODEL,
            trigger=("messages",constant.TRIGGER_MESSAGE_COUNT),
            keep=("messages",constant.KEEP_MESSAGE_COUNT)
        )
    ]
    )

@app.route('/agentic_ai/bus_booking',methods=['GET','POST'])
def bus_booking_api():

    some_json = request.get_json()
    thread_id = some_json['thread_id']
    user_id = some_json['user_id']
    query = some_json['query']
    llm_model = some_json['model']

    if llm_model=='ollama':
        print('ollama selected...')
        # response = model_ollama.invoke(query)
        output = {"response": "work in progress"}
    elif llm_model=='openai':
        print('openai selected...')
        #response = agent.invoke({"messages":[{"role":"user","content":query}]},{"configurable": {"thread_id": thread_id}})
        response = agent.invoke(
            #{"messages":[HumanMessage(content=query)],"user_id":user_id,"booking_status":"pending"},
            {"messages":[HumanMessage(content=query)]},
            {"configurable": {"thread_id": thread_id,"user_id":user_id,"user_name":"Prahi Jayswal"}},
            context=context_schema(user_name="Prahi Jayswal")
        )
        #print(len(response['messages']))
        #print(response['messages'])
        response = response['messages'][-1].content
        output = {"response": response}

    return jsonify(output)

@app.route('/agentic_ai/pass_booking',methods=['GET','POST'])
def pass_booking_api():
    #accepting razor pay payment webhook success/fail payment status
    if request.method == "GET":
        payment_id = request.args.get("razorpay_payment_id")
        payment_link_id = request.args.get("razorpay_payment_link_id")
        reference_id = request.args.get("razorpay_payment_link_reference_id")
        payment_status = request.args.get("razorpay_payment_link_status")
        signature = request.args.get("razorpay_signature")

        print("Payment ID:", payment_id)
        print("Payment Link ID:", payment_link_id)
        print("Reference ID:", reference_id)
        print("Status:", payment_status)
        print("Signature:", signature)

        # Verify payment (recommended)
        # Update booking status
        # Redirect or show success page
        pass_booking.mark_booking_status(conn,payment_link_id=payment_link_id,payment_id=payment_id,payment_status=payment_status)
        booking_data = pass_booking.get_booking_by_payment_link_id(conn,payment_link_id)
        account_id = booking_data['account_id']
        phone = booking_data['phone']
        booking_id = booking_data['booking_id']
        amount = str(booking_data['amount'])
        booking_details = json.loads(booking_data['booking_details'])
        silver = booking_details.get("silver", 0)
        gold = booking_details.get("gold", 0)
        platinum = booking_details.get("platinum", 0)
        date_of_event = booking_details.get("date_of_event", 0)
        if payment_status=="paid":
            #response = f"Thanks for the booking, Your Booking ID {booking_id} is confirmed for {silver}-silver , {gold}-gold , {platinum}-platinum of totalling {amount} INR on date {date_of_event}"
            response = f"""🎉 **Booking Confirmed!** 🎟️

            🙏 Thank you for booking with **Dandiya Mahotsav 2026!** 💃🕺

            ✅ **Booking ID:** {booking_id}

            🎫 **Pass Details:**
            🥈 Silver: {silver} pass(es)
            🥇 Gold: {gold} pass(es)
            💎 Platinum: {platinum} pass(es)

            💰 **Total Amount:** ₹{amount}
            📅 **Event Date:** {date_of_event}

            🎊 Your booking is **confirmed**. We look forward to seeing you at **Dandiya Mahotsav 2026!** 💃🕺✨

            🙏 Thank you!
            """
        else:
            response = f"Sorry your Booking is NOT confirmed! Please try again later"
        send_message.send_whatsapp_message(phone,response,account_id)
        qr_filename = generate_booking_qr(booking_id)
        qr_url = "http://13.201.46.81/QRCodes/"+str(qr_filename)
        print(qr_url)
        send_message.send_whatsapp_image(phone,qr_url,account_id,"Your Ticket QR Code for Entry")

        return f"""
        <h2>Payment {payment_status.upper()}</h2>
        <p>Payment ID: {payment_id}</p>
        <p>Thank you for your payment.</p>
        """, 200

    some_json = request.get_json()
    
    event = some_json.get("event", "")
    workspace_id = some_json.get("workspaceId", "")
    timestamp = some_json.get("timestamp", "")

    data = some_json.get("data", {})
    conversation_id = data.get("conversationId", "")
    message_id = data.get("messageId", "")
    content = data.get("content", "")
    message_type = data.get("messageType", "")
    media_url = data.get("mediaUrl", "")
    account_id = data.get("accountId", "")

    contact = data.get("contact", {})
    contact_id = contact.get("id", "")
    contact_name = contact.get("name", "")
    phone = contact.get("phone", "")

    
    # thread_id = some_json['thread_id']
    # user_id = some_json['user_id']
    # query = some_json['query']
    # llm_model = some_json['model']
    
    thread_id = contact_id
    user_id = contact_id
    query = content
    llm_model = "openai"

    if llm_model=='ollama':
        print('ollama selected...')
        # response = model_ollama.invoke(query)
        output = {"response": "work in progress"}
    elif llm_model=='openai' and event=="message.inbound":
        #print('openai selected...')
        response = agent_pass_booking.invoke(
            {"messages":[HumanMessage(content=query)]},
            {"configurable": {"thread_id": thread_id,"user_id":user_id,"user_name":contact_name,"phone":phone,"account_id":account_id}},
            context=context_schema(user_name=contact_name)
        )
        #print(len(response['messages']))
        #print(response['messages'])
        response = response['messages'][-1].content
        output = {"response": response}
        send_message.send_whatsapp_message(phone,response,account_id)
    else:
        output = {"response":""}
        print("No need to handle this request")

    return jsonify(output)

@app.route('/agentic_ai/salon_appointment_booking',methods=['POST'])
def salon_appointment_booking_api():

    some_json = request.get_json()
    
    event = some_json.get("event", "")
    workspace_id = some_json.get("workspaceId", "")
    timestamp = some_json.get("timestamp", "")

    data = some_json.get("data", {})
    conversation_id = data.get("conversationId", "")
    message_id = data.get("messageId", "")
    content = data.get("content", "")
    message_type = data.get("messageType", "")
    media_url = data.get("mediaUrl", "")
    account_id = data.get("accountId", "")

    contact = data.get("contact", {})
    contact_id = contact.get("id", "")
    contact_name = contact.get("name", "")
    phone = contact.get("phone", "")
    
    thread_id = contact_id
    user_id = contact_id
    query = content
    llm_model = "openai"

    if llm_model=='ollama':
        print('ollama selected...')
        # response = model_ollama.invoke(query)
        output = {"response": "work in progress"}
    elif llm_model=='openai' and event=="message.inbound":
        #print('openai selected...')
        response = agent_salon_appointment_booking.invoke(
            {"messages":[HumanMessage(content=query)]},
            {"configurable": {"thread_id": thread_id,"user_id":user_id,"user_name":contact_name,"phone":phone,"account_id":account_id}},
            context=context_schema(user_name=contact_name)
        )
        #print(len(response['messages']))
        #print(response['messages'])
        response = response['messages'][-1].content
        output = {"response": response}
        send_message.send_whatsapp_message(phone,response,account_id)
    else:
        output = {"response":""}
        print("No need to handle this request")

    return jsonify(output)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006,debug=True)
