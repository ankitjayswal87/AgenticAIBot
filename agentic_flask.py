import os
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from flask import Flask, jsonify, request, send_file, redirect,has_request_context,make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import json 
import base64
import datetime
import random
import string

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
limiter = Limiter(get_remote_address,app=app,default_limits=["1000 per day", "100 per hour"])

#verify the ticket details and confirm with user
def verify_confirm_ticket(from_city:str,to_city:str,journey_date:str,seats:str)->str:
    """Just verify all details received here"""
    print("JOURNEY_DATE:"+str(journey_date))
    return f"Okay, you are going to book total {seats} tickets from {from_city} to {to_city} on date {journey_date}, Please confirm to book it!"

#ticket booking function
def book_bus_ticket(from_city:str,to_city:str,journey_date:str,seats:str)->str:
    """Book bus ticket between given two cities"""
    print("JOURNEY_DATE:"+str(journey_date))
    return f"Your {seats} tickets are booked from {from_city} to {to_city} on date {journey_date}, Thank you!"

system_prompt="""You are a bus ticket booking agent. Just book ticket between two cities. 
Here required fields are from_city, to_city, journey_date and seats. First collect these information and confirm it with
user via tool verify_confirm_ticket ,if user agrees then only book ticket"""

agent = create_agent(model="gpt-4o-mini",tools=[verify_confirm_ticket,book_bus_ticket],system_prompt=system_prompt,checkpointer=InMemorySaver())


@app.route('/agentic_ai/bus_booking',methods=['GET','POST'])
def bus_booking_api():

    some_json = request.get_json()
    thread_id = some_json['thread_id']
    query = some_json['query']
    llm_model = some_json['model']

    #print("Query:"+str(query)+"\nThreadID:"+str(thread_id)+"\n")

    if llm_model=='ollama':
        print('ollama selected...')
        # response = model_ollama.invoke(query)
        output = {"response": "work in progress"}
    elif llm_model=='openai':
        print('openai selected...')
        response = agent.invoke({"messages":[{"role":"user","content":query}]},{"configurable": {"thread_id": thread_id}})
        response = response['messages'][-1].content
        output = {"response": response}

    #output = {"response": "hello"}
    return jsonify(output)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006,debug=True)