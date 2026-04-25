import os
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent, AgentState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langchain.tools import tool, ToolRuntime
from langchain.agents.middleware import dynamic_prompt, ModelRequest, before_model, after_model, SummarizationMiddleware
from langgraph.runtime import Runtime
from dataclasses import dataclass
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

@dataclass
class Context:
    user_name: str
    
# Dynamic prompts
@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    user_name = request.runtime.context.user_name  
    system_prompt = f"""You are a bus ticket booking agent. Be polite while speaking. Keep your answers short and easy to understand. Just book ticket between two cities. 
Here required fields are from_city, to_city, journey_date and seats. First collect these information and confirm it with
user via tool verify_confirm_ticket ,if user agrees then only book ticket Address the user as {user_name}."""
    return system_prompt

# Before model hook
@before_model
def log_before_model(state: AgentState, runtime: Runtime[Context]) -> dict | None:
    print(f"Processing request for user: {runtime.context.user_name}")
    return None

# After model hook
@after_model
def log_after_model(state: AgentState, runtime: Runtime[Context]) -> dict | None:
    print(f"Completed request for user: {runtime.context.user_name}")
    return None

#verify the ticket details and confirm with user
@tool(return_direct=True)
def verify_confirm_ticket(from_city:str,to_city:str,journey_date:str,seats:str,runtime: ToolRuntime)->str:
    """Just verify all details received here"""
    print("JOURNEY_DATE:"+str(journey_date))
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

agent = create_agent(
    model="gpt-4o-mini",
    tools=[verify_confirm_ticket,book_bus_ticket],
    checkpointer=InMemorySaver(),
    middleware=[
        dynamic_system_prompt,
        log_before_model,
        log_after_model,
        SummarizationMiddleware(
            model="gpt-4o-mini",
            trigger=("messages",10),
            keep=("messages",4)
        )
    ],
    context_schema=Context
    )

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
        #response = agent.invoke({"messages":[{"role":"user","content":query}]},{"configurable": {"thread_id": thread_id}})
        response = agent.invoke({"messages":[HumanMessage(content=query)]},{"configurable": {"thread_id": thread_id}},context=Context(user_name="Prahi Jayswal"))
        #print(len(response['messages']))
        #print(response['messages'])
        response = response['messages'][-1].content
        output = {"response": response}

    #output = {"response": "hello"}
    return jsonify(output)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006,debug=True)
