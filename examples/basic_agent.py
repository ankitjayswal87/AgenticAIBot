import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from datetime import datetime

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

agent = create_agent(model="gpt-4o-mini",tools=[book_bus_ticket],system_prompt=system_prompt,checkpointer=InMemorySaver())
response=agent.invoke({"messages":[{"role":"user","content":"from Ahmedabad to Udaipur and on 26th January 2026"}]},{"configurable": {"thread_id": "1"}})

# Sample Response

# {'messages': [HumanMessage(content='book a ticket from Ahmedabad to Jaipur', additional_kwargs={}, response_metadata={}, id='b5aec049-1127-439e-9eca-244894c4327d'),
# AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 23, 'prompt_tokens': 74, 'total_tokens': 97, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_29330a9688', 'id': 'chatcmpl-CsNFl0bSDaZ2vJ04zM8HgpxxHejso', 'service_tier': 'default', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--019b6de2-b11a-7f72-ac97-c468305651d6-0',
# tool_calls=[{'name': 'book_bus_ticket', 'args': {'from_city': 'Ahmedabad', 'to_city': 'Jaipur'}, 'id': 'call_2GSWBK53djbn4pErXuz4gwEe', 'type': 'tool_call'}], usage_metadata={'input_tokens': 74, 'output_tokens': 23, 'total_tokens': 97, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}}),
# ToolMessage(content='Your ticket is booked from Ahmedabad to Jaipur , Thank you!', name='book_bus_ticket', id='5400bcc1-bb9e-48ad-a566-fb2c6c3e6f9f', tool_call_id='call_2GSWBK53djbn4pErXuz4gwEe'),
# AIMessage(content='Your ticket has been successfully booked from Ahmedabad to Jaipur. Thank you!', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 15, 'prompt_tokens': 118, 'total_tokens': 133, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_29330a9688', 'id': 'chatcmpl-CsNFmw7ZbXa1CxufxkHUad8UHTkQy', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--019b6de2-bc27-78c2-a2fd-009efaef92a0-0', usage_metadata={'input_tokens': 118, 'output_tokens': 15, 'total_tokens': 133, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})]}
print(response['messages'][-1].content)
response=agent.invoke({"messages":[{"role":"user","content":"total 4 seats only"}]},{"configurable": {"thread_id": "1"}})
print(response['messages'][-1].content)
response=agent.invoke({"messages":[{"role":"user","content":"yes, details are ok"}]},{"configurable": {"thread_id": "1"}})
print(response['messages'][-1].content)