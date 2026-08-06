# backend/parser.py
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_core.documents import Document  # Modern import path

# Map file extensions to LangChain's supported Language enum values
EXTENSION_TO_LANGUAGE = {
    ".py": Language.PYTHON,
    ".js": Language.JS,
    ".ts": Language.TS,
    ".java": Language.JAVA,
    ".cpp": Language.CPP,
    ".c": Language.C,
    ".go": Language.GO,
    ".html": Language.HTML,
}

def parse_and_chunk_repo(repo_path: str) -> list[Document]:
    """
    Traverses the repository directory, finds supported code files, 
    and chunks them using language-specific syntax splitters.
    """
    all_chunks = []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip hidden directories like .git
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            
            if file_ext in EXTENSION_TO_LANGUAGE:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        code_content = f.read()
                    
                    # Skip empty files
                    if not code_content.strip():
                        continue
                        
                    # Initialize the specific text splitter for this programming language
                    lang = EXTENSION_TO_LANGUAGE[file_ext]
                    splitter = RecursiveCharacterTextSplitter.from_language(
                        language=lang,
                        chunk_size=1000,     # Target characters per chunk
                        chunk_overlap=100    # Maintain context between cuts
                    )
                    
                    # Split the code into chunks
                    texts = splitter.split_text(code_content)
                    
                    # Convert raw text chunks into Document objects with rich metadata
                    for idx, text in enumerate(texts):
                        doc = Document(
                            page_content=text,
                            metadata={
                                "source": relative_path,
                                "language": lang.value,
                                "chunk_id": f"{relative_path}_{idx}"
                            }
                        )
                        all_chunks.append(doc)
                        
                except Exception as e:
                    print(f"Error parsing file {file_path}: {e}")
                    
    return all_chunks