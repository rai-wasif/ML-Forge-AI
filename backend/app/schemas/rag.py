from pydantic import BaseModel, Field


class RagIndexResponse(BaseModel):
    collection: str
    documents: int
    chunks: int
    indexed: int
    embedding_backend: str
    sources: list[str]


class RagSource(BaseModel):
    score: float
    text: str
    source: str
    title: str
    page: int | None = None
    chunk_id: int | str | None = None
    document_type: str = ""


class RagQueryRequest(BaseModel):
    question: str = Field(min_length=3)
    collection: str = "mlforge_docs"
    top_k: int = Field(default=5, ge=1, le=10)


class RagQueryResponse(BaseModel):
    question: str
    answer: str
    collection: str
    sources: list[RagSource]


class RagCollectionsResponse(BaseModel):
    collections: list[str]


class RagDeleteResponse(BaseModel):
    collection: str
    deleted: bool
