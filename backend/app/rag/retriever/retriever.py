from app.rag.config import DEFAULT_COLLECTION
from app.rag.embeddings.embedder import EmbeddingProvider
from app.rag.vector_store.qdrant_store import QdrantVectorStore


def retrieve(question: str, collection_name: str = DEFAULT_COLLECTION, top_k: int = 5) -> list[dict]:
    embedder = EmbeddingProvider()
    vector = embedder.embed_query(question)
    store = QdrantVectorStore()
    try:
        return store.search(collection_name, vector, top_k)
    finally:
        store.close()
