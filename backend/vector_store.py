import os
import hashlib
from pathlib import Path

import chromadb


DEFAULT_DB_PATH = "database/chroma_db"


class CodeVectorStore:
    """
    Persistent ChromaDB vector store for code chunks.
    """

    def __init__(
        self,
        persist_directory: str = DEFAULT_DB_PATH,
        collection_name: str = "code_chunks",
    ):
        self.persist_directory = Path(persist_directory)

        # Make sure the path is a directory, not a file.
        if self.persist_directory.exists():
            if not self.persist_directory.is_dir():
                raise ValueError(
                    f"ChromaDB path exists but is not a directory: "
                    f"{self.persist_directory}"
                )

        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Initialize persistent ChromaDB client.
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        # Create or load the collection.
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "hnsw:space": "cosine"
            },
        )

    def add_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> None:
        """
        Add code chunks and their embeddings to ChromaDB.

        Args:
            chunks: Parsed code chunks.
            embeddings: Gemini embeddings corresponding
                to each chunk.
        """

        if not chunks:
            return

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embeddings."
            )

        ids = []
        documents = []
        metadatas = []

        for chunk, embedding in zip(chunks, embeddings):
            metadata = chunk["metadata"]

            # Generate a deterministic ID for the chunk.
            chunk_id = self._create_chunk_id(
                metadata=metadata,
            )

            ids.append(chunk_id)
            documents.append(chunk["content"])

            # ChromaDB metadata values should be simple
            # serializable types.
            metadatas.append(
                {
                    "file_name": str(
                        metadata["file_name"]
                    ),
                    "file_path": str(
                        metadata["file_path"]
                    ),
                    "language": str(
                        metadata["language"]
                    ),
                    "type": str(
                        metadata["type"]
                    ),
                    "name": str(
                        metadata["name"]
                    ),
                    "parent_class": str(
                        metadata["parent_class"] or ""
                    ),
                    "parent_function": str(
                        metadata["parent_function"] or ""
                    ),
                    "start_line": int(
                        metadata["start_line"]
                    ),
                    "end_line": int(
                        metadata["end_line"]
                    ),
                }
            )

        # Upsert allows the same chunk to be updated
        # instead of creating duplicates.
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> dict:
        """
        Search for the most relevant code chunks.

        Args:
            query_embedding: Gemini embedding of the
                user's question.
            top_k: Number of results to return.

        Returns:
            ChromaDB query results.
        """

        if not query_embedding:
            raise ValueError(
                "Query embedding cannot be empty."
            )

        if top_k < 1:
            raise ValueError(
                "top_k must be at least 1."
            )

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

    def count(self) -> int:
        """
        Return the number of stored code chunks.
        """

        return self.collection.count()
    
    def get_existing_chunk_ids(
    self,
    chunks: list[dict],
    ) -> set[str]:
    """
    Return the IDs of chunks that already exist
    in ChromaDB.
    """

    if not chunks:
        return set()

    chunk_ids = [
        self._create_chunk_id(
            chunk["metadata"]
        )
        for chunk in chunks
    ]

    result = self.collection.get(
        ids=chunk_ids
    )

    return set(result["ids"])

    def clear(self) -> None:
        """
        Delete all stored chunks from the collection.
        """

        collection_name = self.collection.name

        self.client.delete_collection(
            collection_name
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "hnsw:space": "cosine"
            },
        )

    @staticmethod
    def _create_chunk_id(metadata: dict) -> str:
        """
        Create a deterministic ID for a code chunk.

        The ID is based on:
        - file path
        - start line
        - end line
        - code element name

        This makes the same logical code chunk receive
        the same ID across repeated indexing operations.
        """

        raw_id = (
            f"{metadata['file_path']}:"
            f"{metadata['start_line']}:"
            f"{metadata['end_line']}:"
            f"{metadata['name']}"
        )

        return hashlib.sha256(
            raw_id.encode("utf-8")
        ).hexdigest()


if __name__ == "__main__":
    store = CodeVectorStore()

    print("ChromaDB initialized successfully.")
    print(
        f"Stored chunks: {store.count()}"
    )
    print(
        f"Database path: "
        f"{os.path.abspath(DEFAULT_DB_PATH)}"
    )