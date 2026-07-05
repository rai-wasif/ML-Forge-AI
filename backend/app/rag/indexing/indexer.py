from pathlib import Path

from app.rag.chunking.splitter import chunk_documents
from app.rag.config import DEFAULT_COLLECTION, KNOWLEDGE_BASE_DIR, REPORTS_DIR
from app.rag.embeddings.embedder import EmbeddingProvider
from app.rag.loaders.document_loader import SUPPORTED_EXTENSIONS, load_documents
from app.rag.vector_store.qdrant_store import QdrantVectorStore


def index_documents(
    paths: list[Path],
    collection_name: str = DEFAULT_COLLECTION,
    include_knowledge: bool = True,
    include_reports: bool = True,
) -> dict:
    all_paths = list(paths)

    if include_knowledge:
        all_paths.extend(discover_files(KNOWLEDGE_BASE_DIR))

    if include_reports:
        all_paths.extend(discover_files(REPORTS_DIR))

    unique_paths = sorted({path.resolve() for path in all_paths if path.exists()})
    documents = load_documents(unique_paths)
    chunks = chunk_documents(documents)
    embedder = EmbeddingProvider()
    embeddings = embedder.embed_texts([chunk["text"] for chunk in chunks])
    store = QdrantVectorStore()

    try:
        indexed = store.upsert_chunks(collection_name, chunks, embeddings)
    finally:
        store.close()

    return {
        "collection": collection_name,
        "documents": len(documents),
        "chunks": len(chunks),
        "indexed": indexed,
        "embedding_backend": embedder.backend,
        "sources": [str(path) for path in unique_paths],
    }


def discover_files(root: Path) -> list[Path]:
    if not root.exists():
        return []

    return [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
