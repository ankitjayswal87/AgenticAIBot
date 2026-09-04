from dataclasses import dataclass
#from pydantic import BaseModel

@dataclass
class Context:
    user_name: str

# class Context(BaseModel):
#     user_name: str