from pathlib import Path

from app.rag.indexing.indexer import index_documents
from app.rag.query_engine.query_engine import answer_question


def index_paths(paths: list[str], collection_name: str, include_knowledge: bool, include_reports: bool) -> dict:
    return index_documents(
        [Path(path) for path in paths],
        collection_name=collection_name,
        include_knowledge=include_knowledge,
        include_reports=include_reports,
    )


def query_knowledge(question: str, collection_name: str, top_k: int) -> dict:
    return answer_question(question, collection_name, top_k)
