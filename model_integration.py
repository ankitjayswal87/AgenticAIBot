import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_API_KEY"]=os.getenv("GOOGLE_API_KEY")

from langchain.chat_models import init_chat_model

# loading chatgpt model
# model = init_chat_model("gpt-4.1")
# response = model.invoke("Who is the most trending cricketer of team India from GenZ? Give name only")
# print(response.content)

# loading Gemini model
model = init_chat_model("google_genai:gemini-2.5-flash")
response = model.invoke("Who is the most trending cricketer of team India from GenZ? Give name only")
print(response.content)

# streaming model output
# model = init_chat_model("google_genai:gemini-2.5-flash")
# for chunk in model.stream("what is the role of ISRO in space sector, describe in ten lines"):
#     print(chunk.text, end="|", flush=True)