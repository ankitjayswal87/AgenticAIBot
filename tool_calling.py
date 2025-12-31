import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_API_KEY"]=os.getenv("GOOGLE_API_KEY")

from langchain.chat_models import init_chat_model
from langchain.tools import tool

@tool
def get_weather(location:str)->str:
    """Get weather for the given location"""
    return f"It's sunny in {location}"

model = init_chat_model("gpt-4.1")
model_with_tools = model.bind_tools([get_weather])
response = model_with_tools.invoke("What is the weather in Ahmedabad")
print(response)