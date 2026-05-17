import os
import warnings
import logging

# SILENCE WARNINGS
warnings.filterwarnings("ignore")
logging.getLogger("google").setLevel(logging.ERROR)

from langchain_google_genai import ChatGoogleGenerativeAI
from state import AgentState
from dotenv import load_dotenv

load_dotenv()

# FIX 1: Removed transport="rest" as GitHub Actions (Linux) doesn't need the Mac fix.
# This avoids the 'Unexpected argument' error.
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

def node_analyst(state: AgentState):
    print("🧠 Node: Analyst is studying the code...")
    prompt = f"Analyze this git diff and context:\nContext: {state['context']}\nDiff: {state['diff']}"
    response = llm.invoke(prompt)
    return {"analysis": response.content}

def node_writer(state: AgentState):
    print("📝 Node: Writer is drafting the PR description...")
    prompt = f"Create a professional GitHub PR body based on this analysis:\n{state['analysis']}"
    response = llm.invoke(prompt)
    
    # Extract text from the response safely
    content = response.content
    if isinstance(content, list):
        content = "\n".join([c['text'] if isinstance(c, dict) and 'text' in c else str(c) for c in content])
    
    return {"draft": content}

def node_critic(state: AgentState):
    print("🧐 Node: Critic is auditing the draft...")
    prompt = f"Review this PR Draft against the Diff. Reply 'PASS' if good.\nDiff: {state['diff']}\nDraft: {state['draft']}"
    response = llm.invoke(prompt)
    
    # Extract text safely
    content = response.content
    if isinstance(content, list):
        content = " ".join([c['text'] if isinstance(c, dict) and 'text' in c else str(c) for c in content])
    
    return {"critic_feedback": content.strip()}