# backend/vector_store.py
import os
import shutil
import stat
import time  # Imported for sleep delay
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.ingester import clone_repository
from backend.parser import parse_and_chunk_repo

PERSIST_DB_DIR = "./chroma_db"

def remove_readonly(func, path, _):
    """
    Error handler for shutil.rmtree on Windows.
    Clears the read-only attribute of a file and retries the deletion.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

def cleanup_temp_dir(path: str):
    """
    Safely deletes a directory, handling Windows read-only file lock issues.
    """
    if path and os.path.exists(path):
        print(f"Cleaning up temporary cloned files in {path}...")
        try:
            shutil.rmtree(path, onerror=remove_readonly)
        except Exception as e:
            print(f"Warning: Could not completely delete temp directory: {e}")

def get_embedding_model() -> GoogleGenerativeAIEmbeddings:
    """
    Initializes and returns the current Google Gemini embedding model.
    """
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError(
            "GOOGLE_API_KEY environment variable is missing. "
            "Please set it in your environment before running."
        )
    return GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

def initialize_github_vector_store(repo_url: str):
    """
    Real backend pipeline: clones, parses language syntax, embeds with Gemini, and saves to ChromaDB.
    Includes rate-limiting mitigation for Gemini Free Tier.
    """
    if os.path.exists(PERSIST_DB_DIR):
        print(f"Clearing existing vector store at {PERSIST_DB_DIR}...")
        try:
            shutil.rmtree(PERSIST_DB_DIR, onerror=remove_readonly)
        except Exception as e:
            print(f"Warning: Could not clear existing DB directory: {e}")
        
    temp_dir = None
    try:
        # 1. Clone repo
        temp_dir = clone_repository(repo_url)
        
        # 2. Parse files with language-specific AST/Separators
        documents = parse_and_chunk_repo(temp_dir)
        
        if not documents:
            raise ValueError("No supported code files found in this repository.")
            
        print(f"Successfully chunked code into {len(documents)} document blocks.")
        
        # 3. Build Vector DB using rate-limit-friendly batching
        embeddings = get_embedding_model()
        
        # Initialize an empty Chroma database
        vectorstore = Chroma(
            persist_directory=PERSIST_DB_DIR,
            embedding_function=embeddings
        )
        
        # We upload in batches of 50 documents with a small delay
        batch_size = 50
        delay_seconds = 1.5
        total_docs = len(documents)
        
        print(f"Indexing {total_docs} blocks in batches of {batch_size} to respect Gemini API rate limits (100 requests/minute)...")
        
        for i in range(0, total_docs, batch_size):
            batch = documents[i : i + batch_size]
            print(f"⏳ Indexing batch {i//batch_size + 1}/{(total_docs + batch_size - 1)//batch_size}...")
            vectorstore.add_documents(batch)
            time.sleep(delay_seconds)  # Delay to respect the API limits
            
        print("Embedding generation completed successfully!")
        return vectorstore.as_retriever(search_kwargs={"k": 4})
        
    except Exception as e:
        print(f"An error occurred while initializing the vector store: {e}")
        raise e
        
    finally:
        # 4. Safely clean up cloned files (Windows-proof)
        cleanup_temp_dir(temp_dir)