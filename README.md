# AgenticAIBot
Creating agents with langchain

# Installation
Follow link, https://docs.astral.sh/uv/getting-started/installation/

Install via this command, mine is Linux system
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Restart terminal to take effect of this installation of uv package manager

Go to your home directory or project directory
```
cd /home/ubuntu/
```
```
git clone https://github.com/ankitjayswal87/AgenticAIBot.git
```
```
cd AgenticAIBot
```
```
uv init
```
```
uv venv
```
```
source .venv/bin/activate
```

Now. create requirement.tx file.
```
vim requirement.txt
```

Add below content into requirement.txt file.
```
langchain
langchain_community
langchain-openai
langchain-groq
python-dotenv
langchain-google-genai
flask
flask_limiter
faiss-cpu
pymupdf
```
Run command below to install these packages from txt file.
```
uv add -r requirement.txt
```

Export OpenAI API key
```
export OPENAI_API_KEY="sk-xxx"
```

Goto app folder and run main file as below
```
cd app
```
```
python3 main.py
```
Now, your AI agent is running and you can use it via below CURL requests:
```
curl -X POST 'http://localhost:5006/agentic_ai/bus_booking' --header 'Content-Type: application/json' --data-raw '{"thread_id":"call123abc","user_id":"test123","query":"Hello, I want to book 2 seats from Ahmedabad to Mumbai","model":"openai"}'
```

It will respond you something like:
```
{
  "response": "Sure, Prahi Jayswal! Could you please provide me with the journey date for your trip from Ahmedabad to Mumbai?"
}
```

Great, you successfully deployed Ticket booking AI Agent. You can now play with it and it will respond you accordingly. 
