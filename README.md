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
cd /home/ankit/agentic_ai
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
```

Make below commands to setup flask.
```
uv add flask
uv add flask_limiter
```

Create .env file also in project folder.
```
vim .env
```
Add below content into .env file.
```
OPENAI_API_KEY=""
GOOGLE_API_KEY=""
```
