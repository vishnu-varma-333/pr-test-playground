import os
import warnings
import logging

# 1. Suppress Python Warnings
warnings.filterwarnings("ignore")
# 2. Suppress Google/gRPC Logging
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["GRPC_VERBOSITY"] = "ERROR"
logging.getLogger("google").setLevel(logging.ERROR)

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from state import AgentState
from dotenv import load_dotenv

load_dotenv()

# Initialize our LLM (Gemini)
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    transport="rest",
    temperature=0
)

def node_analyst(state: AgentState):
    """Analyze the code diff and explain the logic changes."""
    print("🧠 Node: Analyst is studying the code...")
    
    prompt = f"""
    You are an expert Lead Developer. Review this code change and the context.
    Explain WHAT changed and WHY it was changed based on commit messages.
    
    Context: {state['context']}
    Diff: {state['diff']}
    
    Focus on logic changes, new functions, or security concerns. 
    Keep it technical but concise.
    """
    
    response = llm.invoke(prompt)
    return {"analysis": response.content}

def node_writer(state: AgentState):
    """Take the analysis and write a professional PR body."""
    print("📝 Node: Writer is drafting the PR description...")
    
    prompt = f"""
    You are a technical writer. Create a professional GitHub Pull Request body.
    Use the following analysis to structure your response.
    
    Analysis: {state['analysis']}
    
    Use this Markdown structure:
    ## 🚀 Summary
    (One sentence explaining the main goal)
    
    ## 🛠️ Key Changes
    (Bullet points of technical changes)
    
    ## 🧪 Testing
    (Suggest how a reviewer should test this)
    """
    
    response = llm.invoke(prompt)
    return {"draft": response.content}

def node_critic(state: AgentState):
    """The Auditor: Checks if the draft is missing anything."""
    print("🧐 Node: Critic is auditing the draft...")
    
    # We compare the draft against the original diff
    prompt = f"""
    Compare this PR Draft with the original Diff. 
    Does the draft accurately represent the code? 
    Is it missing any files or important logic?
    
    Original Diff: {state['diff']}
    Current Draft: {state['draft']}
    
    If it's good, reply with 'PASS'. 
    If not, provide brief feedback on what is missing.
    """
    
    response = llm.invoke(prompt)
    # If the LLM says anything other than 'PASS', we store it as feedback
    feedback = response.content.strip()
    return {"critic_feedback": feedback}