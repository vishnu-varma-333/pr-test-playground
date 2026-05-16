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
from tools import fetch_pr_data
from graph import app

def run_pr_agent(repo: str, pr_num: int):
    # 1. Fetch raw data
    print(f"🚀 Starting Agent for {repo} PR #{pr_num}...")
    raw_data = fetch_pr_data(repo, pr_num)
    
    # 2. Initialize State
    initial_state = {
        "repo_id": repo,
        "pr_number": pr_num,
        "diff": raw_data["diff"],
        "context": raw_data["context"],
        "revision_count": 0
    }
    
    # 3. Run the LangGraph Agent!
    final_output = app.invoke(initial_state)
    
    print("\n" + "="*50)
    print("🔥 FINAL GENERATED PR BODY:")
    print("="*50 + "\n")
    print(final_output["draft"])
    
    # NEW: Ask the user to push to GitHub
    confirm = input("\n🚀 Would you like to push this description to GitHub? (y/n): ")
    if confirm.lower() == 'y':
        from tools import update_pr_on_github
        update_pr_on_github(repo, pr_num, final_output["draft"])
    else:
        print("❌ Update cancelled.")

if __name__ == "__main__":
    # When running in GitHub Actions, these variables are provided automatically
    repo = os.getenv("GITHUB_REPOSITORY")  # e.g., "vishnu-varma-333/pr-test-playground"
    
    # GitHub provides the event path, we can extract the PR number from it
    # But an easier way is to pass it as an argument or env var
    pr_num = os.getenv("PR_NUMBER")

    if repo and pr_num:
        print(f"🤖 GitHub Action triggered for {repo} PR #{pr_num}")
        run_pr_agent(repo, int(pr_num))
    else:
        # Fallback for local testing
        print("⚠️ Environment variables not found. Running in local mode...")
        run_pr_agent("your-username/your-repo", 1)