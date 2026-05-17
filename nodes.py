import os
import time
import warnings
import logging
import ssl

# 1. SSL Fix for Mac
ssl._create_default_https_context = ssl._create_unverified_context

# 2. Silence Clutter
warnings.filterwarnings("ignore")
logging.getLogger("google").setLevel(logging.ERROR)

from langchain_google_genai import ChatGoogleGenerativeAI
from state import AgentState
from dotenv import load_dotenv

load_dotenv()

# 3. Setup LLM
is_cloud = os.getenv("GITHUB_ACTIONS") == "true"
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", # Use the stable 1.5 model
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
    transport="rest" if not is_cloud else None # Use rest ONLY for local Mac
)

def safe_invoke(prompt):
    """Simple, clean invoker with basic string handling."""
    # A small 5-second sleep is enough to stay within the 15 RPM limit 
    # without making the script take 10 minutes.
    time.sleep(5) 
    response = llm.invoke(prompt)
    
    # Handle the 'List vs String' response bug
    content = response.content
    if isinstance(content, list):
        content = "\n".join([c['text'] if isinstance(c, dict) and 'text' in c else str(c) for c in content])
    return str(content)

def node_analyst(state: AgentState):
    print("🧠 Node: Analyst is studying the code...")
    prompt = f"Analyze this git diff and context:\nContext: {state['context']}\nDiff: {state['diff']}"
    return {"analysis": safe_invoke(prompt)}

def node_writer(state: AgentState):
    print("📝 Node: Writer is drafting the PR description...")
    prompt = f"Create a professional GitHub PR body based on this analysis:\n{state['analysis']}"
    return {"draft": safe_invoke(prompt)}

def node_critic(state: AgentState):
    print("🧐 Node: Critic is auditing the draft...")
    # In 'Speed mode', we can just have the critic return PASS 
    # to save quota, or keep the audit logic:
    prompt = f"Review this PR Draft against the Diff. Reply 'PASS' if good.\nDiff: {state['diff']}\nDraft: {state['draft']}"
    res = safe_invoke(prompt)
    return {"critic_feedback": res.strip()}