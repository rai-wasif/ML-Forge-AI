from uuid import uuid4

from qdrant_client import QdrantClient, models

from app.rag.config import QDRANT_URL, VECTOR_SIZE


class QdrantVectorStore:
    def __init__(self, url: str = QDRANT_URL) -> None:
        self.client = QdrantClient(url=url, timeout=30)

    def ensure_collection(self, collection_name: str) -> None:
        collections = [item.name for item in self.client.get_collections().collections]
        if collection_name in collections:
            return

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )

    def upsert_chunks(self, collection_name: str, chunks: list[dict], embeddings: list[list[float]]) -> int:
        self.ensure_collection(collection_name)
        points = []

        for chunk, embedding in zip(chunks, embeddings):
            points.append(
                models.PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk["text"],
                        **chunk["metadata"],
                    },
                )
            )

        if points:
            self.client.upsert(collection_name=collection_name, points=points)

        return len(points)

    def search(self, collection_name: str, query_vector: list[float], top_k: int = 5) -> list[dict]:
        self.ensure_collection(collection_name)
        if hasattr(self.client, "search"):
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                with_payload=True,
            )
        else:
            response = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=top_k,
                with_payload=True,
            )
            results = response.points

        return [
            {
                "score": float(item.score),
                "text": item.payload.get("text", ""),
                "source": item.payload.get("source", ""),
                "title": item.payload.get("title", ""),
                "page": item.payload.get("page"),
                "chunk_id": item.payload.get("chunk_id"),
                "document_type": item.payload.get("document_type", ""),
            }
            for item in results
        ]

    def list_collections(self) -> list[str]:
        return [item.name for item in self.client.get_collections().collections]

    def delete_collection(self, collection_name: str) -> None:
        collections = self.list_collections()
        if collection_name in collections:
            self.client.delete_collection(collection_name)

    def close(self) -> None:
        self.client.close()
