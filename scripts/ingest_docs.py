"""
Documentation ingestion script.

Loads local documentation files from a directory, chunks them,
and ingests them into the Pinecone vector store.
"""

from typing import List, Tuple
import os

from app.config.settings import get_settings
from app.infrastructure.vectorstores.pinecone_client import get_vectorstore_client


def load_documents_from_dir(path: str) -> List[Tuple[str, str]]:
    """
    Load text documents from a directory.

    Args:
        path: Directory path containing documentation files.

    Returns:
        List of (doc_name, content) tuples.
    """
    if not os.path.exists(path) or not os.path.isdir(path):
        return []

    documents = []

    for filename in os.listdir(path):
        if not filename.endswith((".txt", ".md")):
            continue

        file_path = os.path.join(path, filename)

        if not os.path.isfile(file_path):
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append((filename, content))
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    return documents


def chunk_document(content: str, max_tokens: int = 500) -> List[str]:
    """
    Split a document's content into smaller chunks.

    Args:
        content: Full text content of the document.
        max_tokens: Approximate maximum size of each chunk.

    Returns:
        List of text chunks.
    """
    if not content or not content.strip():
        return []

    chunks = []

    for i in range(0, len(content), max_tokens):
        chunk = content[i : i + max_tokens]
        chunk = chunk.strip()
        if chunk:
            chunks.append(chunk)

    return chunks


def ingest_documents() -> None:
    """
    High-level ingestion routine.

    - Load settings (e.g., DOCS_DIR)
    - Load documents from the directory
    - Chunk documents
    - Upsert chunks into the vector store with metadata
    """
    settings = get_settings()
    vectorstore = get_vectorstore_client()

    docs = load_documents_from_dir(settings.DOCS_DIR)

    if not docs:
        print(f"No documents found in {settings.DOCS_DIR}")
        return

    print(f"Found {len(docs)} documents to ingest")

    for doc_name, content in docs:
        chunks = chunk_document(content)

        if not chunks:
            print(f"Skipping {doc_name} (no content after chunking)")
            continue

        texts = chunks
        metadatas = [
            {"source": doc_name, "chunk_index": idx} for idx, _ in enumerate(chunks)
        ]
        ids = [f"{doc_name}-{idx}" for idx, _ in enumerate(chunks)]

        vectorstore.upsert_documents(texts=texts, metadatas=metadatas, ids=ids)
        print(f"Ingested {len(chunks)} chunks from {doc_name}")

    print("Ingestion complete")


def main() -> None:
    """
    Entry point for the ingestion script.

    - Call ingest_documents()
    - Provide basic CLI output/logging.
    """
    try:
        ingest_documents()
    except Exception as e:
        print(f"Error during ingestion: {e}")
        raise


if __name__ == "__main__":
    main()
