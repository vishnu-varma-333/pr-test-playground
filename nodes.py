import os
import time
import warnings
import logging
import ssl

# 1. FIX FOR MAC LIBRESSL (Works on Mac & Cloud)
ssl._create_default_https_context = ssl._create_unverified_context

# 2. SILENCE CLUTTER
warnings.filterwarnings("ignore")
logging.getLogger("google").setLevel(logging.ERROR)

from langchain_google_genai import ChatGoogleGenerativeAI
from state import AgentState
from dotenv import load_dotenv

load_dotenv()

# 3. INITIALIZE LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
    max_retries=10
)

def safe_invoke(prompt, retries=5, delay=45):
    # The 'global' declaration must be at the top to avoid SyntaxError
    global llm
    
    for i in range(retries):
        try:
            # Polite delay to stay within the 15 Requests Per Minute limit
            time.sleep(12) 
            
            response = llm.invoke(prompt)
            
            # SAFE DATA EXTRACTION
            content = response.content
            if isinstance(content, list):
                text_parts = []
                for chunk in content:
                    if isinstance(chunk, dict) and 'text' in chunk:
                        text_parts.append(chunk['text'])
                    else:
                        text_parts.append(str(chunk))
                content = "\n".join(text_parts)
            
            return str(content)

        except Exception as e:
            err_str = str(e).upper()
            
            # Handle Quota / Rate Limits
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                print(f"⚠️ Quota hit. Attempt {i+1}/{retries}. Sleeping {delay}s...")
                time.sleep(delay)
                delay *= 1.5 
                continue
            
            # Handle Model Not Found (Fallback)
            elif "404" in err_str:
                print("🔄 Model ID error. Switching to fallback...")
                llm = ChatGoogleGenerativeAI(
                    model="gemini-flash-latest", 
                    google_api_key=os.getenv("GOOGLE_API_KEY")
                )
                continue
                
            else:
                print(f"❌ Unexpected Error: {e}")
                raise e
    
    raise Exception("🛑 Failed after multiple retries.")

def node_analyst(state: AgentState):
    print("🧠 Node: Analyst is studying the code...")
    prompt = f"Analyze this git diff and context:\nContext: {state['context']}\nDiff: {state['diff']}"
    res = safe_invoke(prompt)
    return {"analysis": res}

def node_writer(state: AgentState):
    print("📝 Node: Writer is drafting the PR description...")
    prompt = f"Create a professional GitHub PR body based on this analysis:\n{state['analysis']}"
    res = safe_invoke(prompt)
    return {"draft": res}

def node_critic(state: AgentState):
    print("🧐 Node: Critic is auditing the draft...")
    prompt = f"Review this PR Draft against the Diff. Reply 'PASS' if good.\nDiff: {state['diff']}\nDraft: {state['draft']}"
    res = safe_invoke(prompt)
    return {"critic_feedback": res.strip()}