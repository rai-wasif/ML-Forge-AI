import os

from sklearn.feature_extraction.text import HashingVectorizer

from app.rag.config import VECTOR_SIZE


class EmbeddingProvider:
    def __init__(self) -> None:
        self.backend = "hashing-384"
        self._hf_model = None
        self._vectorizer = HashingVectorizer(
            n_features=VECTOR_SIZE,
            alternate_sign=False,
            norm="l2",
        )

        if os.getenv("MLFORGE_EMBEDDING_BACKEND", "").lower() == "hf":
            self._load_huggingface()

    def _load_huggingface(self) -> None:
        try:
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding

            self._hf_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
            self.backend = "BAAI/bge-small-en-v1.5"
        except Exception:
            self._hf_model = None
            self.backend = "hashing-384"

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if self._hf_model is not None:
            return [self._hf_model.get_text_embedding(text) for text in texts]

        return self._vectorizer.transform(texts).toarray().astype(float).tolist()

    def embed_query(self, question: str) -> list[float]:
        return self.embed_texts([question])[0]
