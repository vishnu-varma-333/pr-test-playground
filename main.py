import os
import warnings
import logging
import sys

# 1. Suppress Warnings
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"
logging.getLogger("google").setLevel(logging.ERROR)

# 2. Imports - ADDED update_pr_on_github here!
from tools import fetch_pr_data, update_pr_on_github
from graph import app

def run_pr_agent(repo: str, pr_num: int):
    print(f"🚀 Starting Agent for {repo} PR #{pr_num}...")
    raw_data = fetch_pr_data(repo, pr_num)
    
    initial_state = {
        "repo_id": repo,
        "pr_number": pr_num,
        "diff": raw_data["diff"],
        "context": raw_data["context"],
        "revision_count": 0
    }
    
    final_output = app.invoke(initial_state)
    body = final_output["draft"]

    # Check if we are running inside GitHub Actions
    is_github_action = os.getenv("GITHUB_ACTIONS") == "true"

    if is_github_action:
        print("🤖 Running in GitHub Actions. Pushing description automatically...")
        update_pr_on_github(repo, pr_num, body)
    else:
        print("\n" + "="*50)
        print(body)
        print("="*50)
        confirm = input("\n🚀 Local mode: Push to GitHub? (y/n): ")
        if confirm.lower() == 'y':
            update_pr_on_github(repo, pr_num, body)

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