from dataclasses import dataclass

@dataclass
class Context:
    user_name: str
    
@dataclass
class ContextAPIValidation:
    api_host: str
    api_name: str
    request_id: str