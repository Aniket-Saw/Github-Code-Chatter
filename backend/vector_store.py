# backend/vector_store.py

class MockRetriever:
    """
    A temporary mock retriever so Partner B can build the frontend 
    and LLM chain before the backend is fully completed.
    """
    def get_relevant_documents(self, query: str):
        # Returns mock Document objects resembling real code chunks
        class MockDocument:
            def __init__(self, page_content, metadata):
                self.page_content = page_content
                self.metadata = metadata
                
        return [
            MockDocument(
                page_content="def authenticate_user(username, password):\n    # Mock auth logic\n    return True",
                metadata={"source": "auth.py", "language": "python"}
            ),
            MockDocument(
                page_content="def get_db_connection():\n    return psycopg2.connect(dsn)",
                metadata={"source": "db.py", "language": "python"}
            )
        ]

def initialize_github_vector_store(repo_url: str):
    """
    Partner A will eventually implement the real logic here.
    For now, it returns a mock retriever to not block Partner B.
    """
    print(f"Mocking ingestion for: {repo_url}")
    return MockRetriever()