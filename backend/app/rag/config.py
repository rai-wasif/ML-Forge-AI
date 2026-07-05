from pathlib import Path


DEFAULT_COLLECTION = "mlforge_docs"
QDRANT_URL = "http://localhost:6333"
VECTOR_SIZE = 384

RAG_ROOT = Path(__file__).resolve().parent
KNOWLEDGE_BASE_DIR = RAG_ROOT / "knowledge_base"
UPLOAD_DIR = KNOWLEDGE_BASE_DIR / "uploads"
REPORTS_DIR = Path(__file__).resolve().parents[1] / "storage" / "reports"
