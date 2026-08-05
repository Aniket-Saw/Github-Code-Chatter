# backend/test_pipeline.py
import os
import sys

# Ensure Python can resolve paths inside backend/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.vector_store import initialize_github_vector_store

def run_backend_test():
    print("=== STARTING BACKEND PIPELINE VERIFICATION ===\n")
    
    # 1. Quick environment check
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY environment variable is not set.")
        return
    else:
        print("✅ Environment Check: GOOGLE_API_KEY found.")

    # 2. Tiny repository containing a single Python script for fast testing
    test_repo = "https://github.com/audzeimar/python-file-organizer" 
    print(f"🔗 Target Repository: {test_repo}\n")

    try:
        # 3. Call your core backend pipeline function
        print("⏳ Running pipeline...")
        retriever = initialize_github_vector_store(test_repo)
        print("✅ Pipeline executed successfully!\n")

        # 4. Test Query Retrieval
        test_query = "sorting files or folder path"
        print(f"🔍 Testing Search Query: '{test_query}'")
        print("⏳ Querying local ChromaDB...")
        
        # Modern, unified LangChain method
        retrieved_docs = retriever.invoke(test_query)
        print(f"✅ Found {len(retrieved_docs)} matching code blocks.\n")
        
        # 5. Display Retrieved Chunk Metadata & Snippet Content
        print("=== RETRIEVED BLOCKS (DIAGNOSTIC OUTPUT) ===")
        for idx, doc in enumerate(retrieved_docs):
            print(f"\n--- MATCH {idx + 1} ---")
            print(f"📂 File: {doc.metadata.get('source')}")
            print(f"🔤 Language: {doc.metadata.get('language')}")
            print(f"🆔 Chunk ID: {doc.metadata.get('chunk_id')}")
            print(f"✂️ Fragment (First 150 chars):\n")
            print(doc.page_content[:150].strip() + "\n...")
            print("-" * 30)

    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")

if __name__ == "__main__":
    run_backend_test()