````markdown
# 📂 GitHub Repository Code Chatter (Backend Integration Guide)

This guide outlines how **Partner B** can call and utilize the backend data pipeline built by **Partner A**. The backend handles repository ingestion, AST-based parsing, local Chroma vector database creation, and vector retrieval.

---

## 🛠️ 1. Installation & Environment Setup

Before running the application, ensure you have your virtual environment activated and the required packages installed:

```bash
# Install all required packages
pip install -r requirements.txt
```
````

### Configure the Gemini API Key

The pipeline uses **Google Gemini** for embeddings (`gemini-embedding-2-preview`). You must export your Gemini API key:

- **Windows (PowerShell):** `$env:GOOGLE_API_KEY="AIzaSy..."`
- **Windows (CMD):** `set GOOGLE_API_KEY="AIzaSy..."`
- **Mac/Linux:** `export GOOGLE_API_KEY="AIzaSy..."`

---

## 🚀 2. How to Use the Backend Code

You can import and initialize the vector store from any file (e.g., your `frontend/app.py` script) with a single function call.

```python
from backend.vector_store import initialize_github_vector_store

# 1. Provide the repository URL
repo_url = "https://github.com/audzeimar/python-file-organizer"

# 2. Initialize the Vector Store Retriever
# (This clones, splits the code, embeds, and saves to local Chroma DB)
retriever = initialize_github_vector_store(repo_url)

# 3. Retrieve relevant code blocks based on a user's prompt
user_query = "How is folder organization handled?"
retrieved_docs = retriever.invoke(user_query)

# 4. Each returned doc in the list contains page_content and metadata
for doc in retrieved_docs:
    print(f"File Path: {doc.metadata['source']}")
    print(f"Language: {doc.metadata['language']}")
    print(f"Code Snippet:\n{doc.page_content}\n")
```

---

## 📦 3. Behind the Scenes Details

- **Language-Aware Chunking:** The parser (`backend/parser.py`) automatically detects supported languages (Python, JavaScript, TypeScript, Java, C/C++, Go, HTML) and uses LangChain's native recursive language splitters.
- **Rate-Limit Safe Ingestion:** Ingestion handles rate limits on the Gemini API by batching chunk uploads with defensive delays.
- **Storage Location:** Chroma DB files are persisted locally in the `./chroma_db` folder of the workspace.

---

## 🤝 4. Contributing & Git Workflow

Follow this step-by-step workflow to contribute to the repository using a fork and pull request (PR):

### 1. Clone your fork and navigate into the project
```bash
git clone https://github.com/YOUR-USERNAME/YOUR-FORKED-REPO.git
cd YOUR-FORKED-REPO
```

### 2. Add the original repository as `upstream`
```bash
git remote add upstream https://github.com/ORIGINAL-OWNER/ORIGINAL-REPO.git
```

### 3. Fetch latest changes from original `main` and sync local `main`
```bash
git checkout main
git fetch upstream
git reset --hard upstream/main
```

### 4. Create and switch to a new feature branch
```bash
git checkout -b my-feature-branch
```

### 5. Make your code changes, stage, and commit them
```bash
git add .
git commit -m "Description of changes"
```

### 6. Push your branch to YOUR fork
```bash
git push origin my-feature-branch
```

### 7. Create a Pull Request (PR) to the original repository
```bash
gh pr create --repo ORIGINAL-OWNER/ORIGINAL-REPO --base main --head YOUR-USERNAME:my-feature-branch --title "Your PR Title" --body "Your PR description"
```

