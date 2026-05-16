import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

# Initialize the GitHub client
g = Github(os.getenv("GITHUB_TOKEN"))

def update_pr_on_github(repo_id: str, pr_number: int, body: str):
    """
    Push the generated Markdown body to the actual GitHub Pull Request.
    """
    repo = g.get_repo(repo_id)
    pr = repo.get_pull(pr_number)
    pr.edit(body=body)
    print(f"✅ Successfully updated PR #{pr_number} on GitHub!")
    
def fetch_pr_data(repo_id: str, pr_number: int):
    """
    Fetches the diff and context (description/commits) for a specific PR.
    """
    repo = g.get_repo(repo_id)
    pr = repo.get_pull(pr_number)
    
    # 1. Fetch the Diff using the compare method
    # We compare the 'base' (where code is going) to the 'head' (your new code)
    comparison = repo.compare(pr.base.sha, pr.head.sha)
    files = comparison.files
    
    diff_text = ""
    for file in files:
        # Patch is the actual lines changed
        patch = file.patch if file.patch else "No changes in content (e.g., file move)"
        diff_text += f"\nFile: {file.filename}\nStatus: {file.status}\n"
        diff_text += f"Patch:\n{patch}\n"

    # 2. Fetch Context (Commits and PR Description)
    commits = pr.get_commits()
    commit_messages = "\n".join([f"- {c.commit.message}" for c in commits])
    
    context = f"PR Title: {pr.title}\n"
    context += f"Initial Description: {pr.body if pr.body else 'No description provided.'}\n"
    context += f"Commit Messages:\n{commit_messages}"
    
    return {
        "diff": diff_text,
        "context": context
    }