import os
import warnings
import logging

# THE SILENCE BLOCK - MUST BE BEFORE ALL OTHER IMPORTS
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["GRPC_VERBOSITY"] = "ERROR"
warnings.filterwarnings("ignore")
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("langchain_google_genai").setLevel(logging.ERROR)

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Using the EXACT model name your discover_models script found
llm = ChatGoogleGenerativeAI(
    model="openai", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    transport="rest"
)

try:
    response = llm.invoke("Say 'System clear and online'")
    print(f"\n✅ Gemini says: {response.content}")
except Exception as e:
    print(f"\n❌ Error: {e}")