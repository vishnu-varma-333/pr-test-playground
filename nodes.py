import os
import time
import warnings
import logging
import ssl

# 1. FIX FOR MAC LIBRESSL (Works on Mac & Cloud)
# This replaces the need for transport="rest"
ssl._create_default_https_context = ssl._create_unverified_context

# 2. SILENCE CLUTTER
warnings.filterwarnings("ignore")
logging.getLogger("google").setLevel(logging.ERROR)

from langchain_google_genai import ChatGoogleGenerativeAI
from state import AgentState
from dotenv import load_dotenv

load_dotenv()

# 3. INITIALIZE STABLE LLM
# We use gemini-1.5-flash (the most stable free model)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
    max_retries=10 # Built-in retry logic
)

def safe_invoke(prompt, retries=5, delay=40):
    """
    The most robust invoker possible. 
    Handles 429 (Quota), 404 (Model Names), and List/String errors.
    """
    for i in range(retries):
        try:
            # Politeness delay to avoid 'Burst' 429 errors
            time.sleep(10) 
            
            response = llm.invoke(prompt)
            
            # SAFE DATA EXTRACTION
            # Handles if Gemini returns a string or a list of blocks
            content = response.content
            if isinstance(content, list):
                # Join only the text parts
                text_parts = []
                for chunk in content:
                    if isinstance(chunk, dict) and 'text' in chunk:
                        text_parts.append(chunk['text'])
                    else:
                        text_parts.append(str(chunk))
                content = "\n".join(text_parts)
            
            return content

        except Exception as e:
            err_str = str(e).upper()
            
            # If we hit a Quota Limit
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                print(f"⚠️ Quota hit. Attempt {i+1}/{retries}. Sleeping {delay}s...")
                time.sleep(delay)
                delay *= 1.5 # Wait even longer next time
                continue
            
            # If we hit a Model Not Found (happens if Google changes IDs)
            elif "404" in err_str:
                print("🔄 Model 1.5-flash not found. Falling back to flash-latest...")
                # Try one fallback model name
                global llm
                llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=os.getenv("GOOGLE_API_KEY"))
                continue
                
            else:
                print(f"❌ Unexpected Error: {e}")
                raise e
    
    raise Exception("🛑 Failed to get response after multiple retries due to Quota limits.")

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