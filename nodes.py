import os
import time
import warnings
import logging

# 1. Total Silence
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("langchain_google_genai").setLevel(logging.ERROR)

from langchain_google_genai import ChatGoogleGenerativeAI
from state import AgentState
from dotenv import load_dotenv

load_dotenv()

# 2. SWITCH MODEL ID: 
# We are using 'gemini-2.0-flash' because your 'gemini-flash-latest' 
# has hit a daily 20-request limit. 
model_to_use = "gemini-2.0-flash" 

is_cloud = os.getenv("GITHUB_ACTIONS") == "true"

llm = ChatGoogleGenerativeAI(
    model=model_to_use,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
    # Standard Linux (Cloud) doesn't like 'transport', Mac needs it.
    transport="rest" if not is_cloud else None 
)

def safe_invoke(prompt, retries=2, delay=20):
    """
    Extremely robust wrapper to handle quota and response types.
    """
    for i in range(retries):
        try:
            # Wait 15 seconds between every single AI thought to be safe
            time.sleep(15) 
            
            response = llm.invoke(prompt)
            
            # Handle if response is a list or string
            content = response.content
            if isinstance(content, list):
                content = "\n".join([c['text'] if isinstance(c, dict) and 'text' in c else str(c) for c in content])
            
            return content

        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg:
                if i < retries - 1:
                    print(f"⚠️ API is busy (429). Sleeping {delay}s and retrying...")
                    time.sleep(delay)
                    continue
                else:
                    print("🛑 Daily Quota Exhausted for this model. Try again tomorrow or change the model name.")
                    raise e
            elif "404" in err_msg:
                print(f"❌ Model '{model_to_use}' not found. Please check spelling.")
                raise e
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