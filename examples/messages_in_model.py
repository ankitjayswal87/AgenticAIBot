import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_API_KEY"]=os.getenv("GOOGLE_API_KEY")

from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage,HumanMessage

model = init_chat_model("gpt-4.1")

messages = [SystemMessage("You are a helpful assistant for Kamailio SIP proxy"),
HumanMessage("let me know which kind of messages the SIP proxy handles")]

response = model.invoke(messages)
print(response.content)