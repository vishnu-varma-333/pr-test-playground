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

# Check if we are in Cloud or Local
is_cloud = os.getenv("GITHUB_ACTIONS") == "true"

# We use gemini-1.5-flash-002 to avoid being auto-upgraded to experimental models
model_name = "gemini-1.5-flash-002" 

llm = ChatGoogleGenerativeAI(
    model=model_name,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
    transport="rest" if not is_cloud else None # Use REST for Mac, default for Cloud
)

def safe_invoke(prompt, retries=3, delay=30):
    """
    Invokes the LLM with exponential backoff for 429 errors.
    """
    for i in range(retries):
        try:
            # Standard delay to stay polite to the API
            time.sleep(10) 
            
            response = llm.invoke(prompt)
            
            # Handle List vs String response
            content = response.content
            if isinstance(content, list):
                content = "\n".join([c['text'] if isinstance(c, dict) and 'text' in c else str(c) for c in content])
            return content

        except Exception as e:
            if "429" in str(e) and i < retries - 1:
                print(f"⚠️ Quota hit. Retrying in {delay} seconds... (Attempt {i+1}/{retries})")
                time.sleep(delay)
                delay *= 2  # Wait longer next time
            else:
                raise e

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