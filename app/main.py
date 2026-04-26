import os
from dotenv import load_dotenv
load_dotenv()

#langchain imports
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import dynamic_prompt, ModelRequest, before_model, after_model, SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver

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

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")

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

#get your tools for app
tools = [tool.verify_confirm_ticket,tool.book_bus_ticket]

#create your agent here
agent = create_agent(
    model=constant.MODEL,
    tools=tools,
    #system_prompt=system_prompt,
    checkpointer=InMemorySaver(),
    state_schema=state_schema,
    context_schema=context_schema,
    middleware=[
        dynamic_system_prompt,
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
            {"messages":[HumanMessage(content=query)],"user_id":"test123","booking_status":"pending"},
            {"configurable": {"thread_id": thread_id}},
            context=context_schema(user_name="Prahi Jayswal")
        )
        #print(len(response['messages']))
        #print(response['messages'])
        response = response['messages'][-1].content
        output = {"response": response}

    #output = {"response": "hello"}
    return jsonify(output)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006,debug=True)
