# 📝 AI-Powered PR Body Generator
### *An Agentic AI approach to automated documentation*

## 🚀 Overview
Writing Pull Request descriptions is often tedious. This project uses **Agentic AI** to automatically analyze code changes (Git Diffs), understand the developer's intent, and write a structured, professional PR description. 

Unlike a simple "Chatbot" prompt, this uses an **Agentic Workflow** built on **LangGraph**. It doesn't just summarize; it analyzes logic, checks for security risks, and verifies its own work before posting.

---

## 🧠 How it Works: The Agentic Flow
This project follows a "Multi-Agent" design pattern. Instead of one long prompt, the task is broken into three specialized "Nodes":

1.  **The Technical Analyst:** Reads the raw `git diff` and commit messages. It identifies what logic changed and if there are any hardcoded secrets or security risks.
2.  **The Technical Writer:** Takes the analysis and formats it into a professional Markdown template (Summary, Key Changes, Test Plan).
3.  **The Auditor (Critic):** Reviews the draft against the original code. If it finds a hallucination or a missing detail, it signals the writer to refine the draft.

**Why this is better than standard AI:**
*   **Context Awareness:** It looks at linked issues and commit history.
*   **Self-Correction:** The "Critic" node ensures high accuracy.
*   **Security Minded:** It automatically flags hardcoded credentials.

---

## 🛠 Tech Stack
*   **Orchestration:** LangGraph (Stateful Multi-Agent Framework)
*   **Brain:** Google Gemini 1.5 Flash (via Google AI Studio)
*   **Database/VCS:** GitHub REST API
*   **Automation:** GitHub Actions (CI/CD)

---

## ⚙️ Setup Instructions for Teammates

If you want to run this project locally or add it to your own repository, follow these steps:

### 1. Prerequisites
*   Python 3.10+
*   A Google Gemini API Key (Get it free at [aistudio.google.com](https://aistudio.google.com/))
*   A GitHub Personal Access Token (PAT) with `repo` permissions.

### 2. Local Installation
```bash
# Clone the repository
git clone https://github.com/vishnu-varma-333/pr-test-playground
cd pr-agent

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install langgraph langchain-google-genai PyGithub python-dotenv
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_key
GITHUB_TOKEN=your_github_pat
```

### 4. Running Locally
To test it on a specific PR:
1. Open `main.py` and update the `REPO` and `PR_NUM` in the `local mode` section.
2. Run: `python main.py`

---

## 🤖 GitHub Actions Automation (The "Zero-Touch" Mode)
The project is configured to run automatically whenever a PR is opened in this repo.

### How to enable it in your repo:
1.  Copy the `.github/workflows/ai-pr-agent.yml` file to your repository.
2.  Go to your GitHub Repo **Settings > Secrets and variables > Actions**.
3.  Add a new secret named `GOOGLE_API_KEY` with your Gemini key.
4.  That’s it! The next time you open a PR, the agent will wake up and write the description for you.

---

## 🛡 Security & Privacy
*   **Private Repos:** This tool works perfectly with private repositories. Since it runs as a GitHub Action or locally on your machine, your code is accessed securely via your Personal Access Token.
*   **Data Handling:** Code diffs are sent to the LLM for analysis but are not used for training the model (when using the API).

---

### Tips for Teammates:
*   **Empty Descriptions:** You can leave the PR description box empty; the AI will fill it in about 60 seconds after you create the PR.
*   **Security Warnings:** If the AI adds a "Security Note," pay attention! It likely found a hardcoded password or a sensitive logic change.



### How to set this up right now:
If you want your team to use it immediately across different repos without copy-pasting code:

1.  **Make your `pr-test-playground` Repo Public** (or internal to your company).
2.  **Tell them to create a `.github/workflows/ai-agent.yml`** in their repo.
3.  **Give them this specific "Remote" code** for their YAML file:
    ```yaml
    name: AI PR Agent
    on:
      pull_request:
        types: [opened]
    jobs:
      run-ai:
        runs-on: ubuntu-latest
        steps:
          - name: Checkout their code
            uses: actions/checkout@v4
          - name: Run YOUR Agent logic from YOUR repo
            uses: vishnu-varma-333/pr-test-playground@main # This runs YOUR code on THEIR PR
            env:
              GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
              GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    ```

**Summary:** They only copy **one small YAML file**. The Python code stays with you. This is how professional "Marketplace" actions work!