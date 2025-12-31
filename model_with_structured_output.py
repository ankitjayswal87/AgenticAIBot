import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_API_KEY"]=os.getenv("GOOGLE_API_KEY")

from langchain.chat_models import init_chat_model
from pydantic import BaseModel,Field

class Movie(BaseModel):
    title:str=Field(description="the title of the movie")
    year:int=Field(description="the movie released in year")
    director:str=Field(description="the director of the movie")
    rating:str=Field(description="the rating movie got out of 10")

model = init_chat_model("gpt-4.1")
model_with_structure = model.with_structured_output(Movie)
response = model_with_structure.invoke("let me know about details of movie border")
print(response)