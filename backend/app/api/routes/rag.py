from fastapi import APIRouter, File, Form, UploadFile

from app.rag.config import DEFAULT_COLLECTION
from app.schemas.rag import (
    RagCollectionsResponse,
    RagDeleteResponse,
    RagIndexResponse,
    RagQueryRequest,
    RagQueryResponse,
)
from app.services import rag_service


router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/index", response_model=RagIndexResponse)
def index_knowledge_base(
    collection: str = Form(default=DEFAULT_COLLECTION),
    include_knowledge: bool = Form(default=True),
    include_reports: bool = Form(default=False),
    files: list[UploadFile] | None = File(default=None),
):
    return rag_service.index_knowledge_base(
        files=files,
        collection=collection,
        include_knowledge=include_knowledge,
        include_reports=include_reports,
    )


@router.post("/query", response_model=RagQueryResponse)
def query_knowledge_base(request: RagQueryRequest):
    return rag_service.query_knowledge(
        question=request.question,
        collection=request.collection,
        top_k=request.top_k,
    )


@router.get("/collections", response_model=RagCollectionsResponse)
def list_collections():
    return rag_service.list_collections()


@router.delete("/collections/{collection_name}", response_model=RagDeleteResponse)
def delete_collection(collection_name: str):
    return rag_service.delete_collection(collection_name)
