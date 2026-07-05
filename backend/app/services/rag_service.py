import re
import shutil
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.rag.config import DEFAULT_COLLECTION, UPLOAD_DIR
from app.rag.indexing.indexer import index_documents
from app.rag.loaders.document_loader import SUPPORTED_EXTENSIONS
from app.rag.query_engine.query_engine import answer_question
from app.rag.vector_store.qdrant_store import QdrantVectorStore


def index_knowledge_base(
    files: list[UploadFile] | None = None,
    collection: str = DEFAULT_COLLECTION,
    include_knowledge: bool = True,
    include_reports: bool = False,
) -> dict:
    uploaded_paths = save_uploaded_documents(files or [])

    try:
        return index_documents(
            paths=uploaded_paths,
            collection_name=normalize_collection_name(collection),
            include_knowledge=include_knowledge,
            include_reports=include_reports,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Knowledge indexing failed: {exc}",
        ) from exc


def query_knowledge(question: str, collection: str = DEFAULT_COLLECTION, top_k: int = 5) -> dict:
    if not question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is required.",
        )

    try:
        return answer_question(
            question=question.strip(),
            collection_name=normalize_collection_name(collection),
            top_k=top_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Knowledge query failed: {exc}",
        ) from exc


def list_collections() -> dict:
    store = QdrantVectorStore()
    try:
        return {"collections": store.list_collections()}
    finally:
        store.close()


def delete_collection(collection: str) -> dict:
    collection_name = normalize_collection_name(collection)
    store = QdrantVectorStore()
    try:
        existing = store.list_collections()
        store.delete_collection(collection_name)
        return {"collection": collection_name, "deleted": collection_name in existing}
    finally:
        store.close()


def save_uploaded_documents(files: list[UploadFile]) -> list[Path]:
    if not files:
        return []

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved_paths = []

    for upload in files:
        filename = Path(upload.filename or "").name
        suffix = Path(filename).suffix.lower()

        if not filename or suffix not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported knowledge file type. Allowed: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
            )

        target_path = unique_upload_path(filename)
        with target_path.open("wb") as output:
            shutil.copyfileobj(upload.file, output)
        saved_paths.append(target_path)

    return saved_paths


def unique_upload_path(filename: str) -> Path:
    stem = Path(filename).stem
    suffix = Path(filename).suffix.lower()
    safe_stem = re.sub(r"[^a-zA-Z0-9_.-]+", "_", stem).strip("._") or "document"
    candidate = UPLOAD_DIR / f"{safe_stem}{suffix}"
    counter = 1

    while candidate.exists():
        candidate = UPLOAD_DIR / f"{safe_stem}_{counter}{suffix}"
        counter += 1

    return candidate


def normalize_collection_name(collection: str | None) -> str:
    value = (collection or DEFAULT_COLLECTION).strip()
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value)
    value = value.strip("_")
    return value or DEFAULT_COLLECTION
