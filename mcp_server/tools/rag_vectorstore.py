"""
RAG Vectorstore Tool for MCP Server.

Manages vector stores for:
- JD skill matching
- Resume skill matching
- GitHub project ranking
- Action verb lookup
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib


def get_vectorstores_path() -> str:
    """Get the base path for vectorstores."""
    return os.getenv("VECTORSTORES_PATH", "./vectorstores")


def get_store_path(store_name: str) -> str:
    """Get the path for a specific vectorstore."""
    return os.path.join(get_vectorstores_path(), store_name)


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Number of overlapping characters
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind(". ")
            if last_period > chunk_size // 2:
                chunk = chunk[:last_period + 1]
                end = start + last_period + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return [c for c in chunks if c]


def compute_doc_id(content: str) -> str:
    """
    Compute a unique ID for a document.
    
    Args:
        content: Document content
        
    Returns:
        Hash-based ID
    """
    return hashlib.md5(content.encode()).hexdigest()[:12]


def create_vectorstore(
    store_name: str,
    documents: List[Dict[str, Any]],
    embedding_model: str = "all-MiniLM-L6-v2"
) -> Dict[str, Any]:
    """
    Create a new vectorstore with documents.
    
    Note: This is a simplified implementation.
    In production, use ChromaDB or FAISS with actual embeddings.
    
    Args:
        store_name: Name of the vectorstore
        documents: List of documents with 'content' and 'metadata'
        embedding_model: Name of the embedding model
        
    Returns:
        Dictionary with store info
    """
    store_path = get_store_path(store_name)
    os.makedirs(store_path, exist_ok=True)
    
    # Store documents with IDs
    docs_with_ids = []
    for doc in documents:
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})
        
        # Chunk the content
        chunks = chunk_text(content)
        
        for i, chunk in enumerate(chunks):
            doc_id = compute_doc_id(f"{content[:100]}_{i}")
            docs_with_ids.append({
                "id": doc_id,
                "content": chunk,
                "metadata": {**metadata, "chunk_index": i},
            })
    
    # Save documents (simplified - no actual embeddings)
    docs_file = os.path.join(store_path, "documents.json")
    with open(docs_file, "w", encoding="utf-8") as f:
        json.dump(docs_with_ids, f, indent=2, ensure_ascii=False)
    
    # Save metadata
    meta_file = os.path.join(store_path, "metadata.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump({
            "store_name": store_name,
            "document_count": len(docs_with_ids),
            "embedding_model": embedding_model,
        }, f, indent=2)
    
    return {
        "store_name": store_name,
        "store_path": store_path,
        "document_count": len(docs_with_ids),
        "chunk_count": len(docs_with_ids),
    }


def add_documents_to_store(
    store_name: str,
    documents: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Add documents to an existing vectorstore.
    
    Args:
        store_name: Name of the vectorstore
        documents: List of documents to add
        
    Returns:
        Dictionary with operation status
    """
    store_path = get_store_path(store_name)
    docs_file = os.path.join(store_path, "documents.json")
    
    # Load existing documents
    existing_docs = []
    if os.path.exists(docs_file):
        with open(docs_file, "r", encoding="utf-8") as f:
            existing_docs = json.load(f)
    
    # Process new documents
    new_docs = []
    for doc in documents:
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})
        
        chunks = chunk_text(content)
        
        for i, chunk in enumerate(chunks):
            doc_id = compute_doc_id(f"{content[:100]}_{i}")
            new_docs.append({
                "id": doc_id,
                "content": chunk,
                "metadata": {**metadata, "chunk_index": i},
            })
    
    # Combine and save
    all_docs = existing_docs + new_docs
    with open(docs_file, "w", encoding="utf-8") as f:
        json.dump(all_docs, f, indent=2, ensure_ascii=False)
    
    return {
        "store_name": store_name,
        "documents_added": len(new_docs),
        "total_documents": len(all_docs),
    }


def query_vectorstore(
    store_name: str,
    query: str,
    top_k: int = 5,
    filter_metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Query a vectorstore for relevant documents.
    
    Note: This is a simplified keyword-based implementation.
    In production, use actual vector similarity search.
    
    Args:
        store_name: Name of the vectorstore
        query: Query string
        top_k: Number of results to return
        filter_metadata: Optional metadata filter
        
    Returns:
        List of matching documents with scores
    """
    store_path = get_store_path(store_name)
    docs_file = os.path.join(store_path, "documents.json")
    
    if not os.path.exists(docs_file):
        return []
    
    with open(docs_file, "r", encoding="utf-8") as f:
        documents = json.load(f)
    
    # Simple keyword-based scoring
    query_terms = set(query.lower().split())
    
    scored_docs = []
    for doc in documents:
        content = doc.get("content", "").lower()
        metadata = doc.get("metadata", {})
        
        # Apply metadata filter
        if filter_metadata:
            match = all(
                metadata.get(k) == v
                for k, v in filter_metadata.items()
            )
            if not match:
                continue
        
        # Calculate simple score (word overlap)
        content_terms = set(content.split())
        overlap = len(query_terms & content_terms)
        
        if overlap > 0:
            # Normalize by query length
            score = overlap / len(query_terms)
            scored_docs.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": metadata,
                "score": score,
            })
    
    # Sort by score and return top_k
    scored_docs.sort(key=lambda x: x["score"], reverse=True)
    return scored_docs[:top_k]


def delete_vectorstore(store_name: str) -> bool:
    """
    Delete a vectorstore.
    
    Args:
        store_name: Name of the vectorstore
        
    Returns:
        True if deleted, False if not found
    """
    import shutil
    
    store_path = get_store_path(store_name)
    
    if os.path.exists(store_path):
        shutil.rmtree(store_path)
        return True
    
    return False


def list_vectorstores() -> List[Dict[str, Any]]:
    """
    List all vectorstores.
    
    Returns:
        List of vectorstore info dictionaries
    """
    base_path = get_vectorstores_path()
    
    if not os.path.exists(base_path):
        return []
    
    stores = []
    for name in os.listdir(base_path):
        store_path = os.path.join(base_path, name)
        if os.path.isdir(store_path):
            meta_file = os.path.join(store_path, "metadata.json")
            if os.path.exists(meta_file):
                with open(meta_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                stores.append(metadata)
    
    return stores


if __name__ == "__main__":
    # Test RAG vectorstore
    print("Testing RAG Vectorstore...")
    
    # Create test store
    test_docs = [
        {
            "content": "Python is a programming language used for machine learning and data science.",
            "metadata": {"source": "test1"},
        },
        {
            "content": "TensorFlow and PyTorch are popular deep learning frameworks.",
            "metadata": {"source": "test2"},
        },
        {
            "content": "Natural language processing involves text analysis and understanding.",
            "metadata": {"source": "test3"},
        },
    ]
    
    result = create_vectorstore("test_store", test_docs)
    print(f"Created store with {result['document_count']} documents")
    
    # Query test
    results = query_vectorstore("test_store", "machine learning python", top_k=2)
    print(f"Query returned {len(results)} results")
    
    for r in results:
        print(f"  Score: {r['score']:.2f} - {r['content'][:50]}...")
    
    # Clean up
    delete_vectorstore("test_store")
    print("RAG Vectorstore tests complete!")
