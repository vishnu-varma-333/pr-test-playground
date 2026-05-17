import os
import time
import warnings
import logging

# Silence Clutter
warnings.filterwarnings("ignore")
logging.getLogger("google").setLevel(logging.ERROR)

from langchain_google_genai import ChatGoogleGenerativeAI
from state import AgentState
from dotenv import load_dotenv

load_dotenv()

# USE THE STABLE 1.5 MODEL (Avoids the 'Gemini 3' daily limit)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    transport="rest",
    temperature=0,
    max_retries=5  # Built-in LangChain retry
)

def safe_invoke(prompt):
    """Helper to prevent Rate Limit (429) errors by sleeping."""
    # The Free Tier allows 15 Requests Per Minute. 
    # Waiting 5 seconds ensures we stay at 12 RPM maximum.
    time.sleep(5) 
    response = llm.invoke(prompt)
    
    # Handle the 'List' vs 'String' issue discovered earlier
    content = response.content
    if isinstance(content, list):
        content = "\n".join([c['text'] if isinstance(c, dict) and 'text' in c else str(c) for c in content])
    return content

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
    prompt = f"Review this PR Draft against the Diff. Reply 'PASS' if good.\nDiff: {state['diff']}\nDraft: {state['draft']}"
    feedback = safe_invoke(prompt)
    return {"critic_feedback": feedback.strip()}