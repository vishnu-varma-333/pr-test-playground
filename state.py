from typing import TypedDict, Annotated, List

class AgentState(TypedDict):
    # Inputs
    repo_id: str          # e.g., "username/repo-name"
    pr_number: int
    
    # Data gathered from GitHub
    diff: str             # The actual code changes
    context: str          # Combined info from commit messages and linked issues
    
    # Agent outputs
    analysis: str         # The technical breakdown of the changes
    draft: str            # The current version of the PR body
    critic_feedback: str  # Feedback from the Auditor node
    
    # Meta-data
    revision_count: int   # To prevent infinite loops in the critic cycle