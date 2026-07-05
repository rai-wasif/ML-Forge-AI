import json
import re
from pathlib import Path

from llama_index.core import Document
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt", ".html", ".json"}


def load_documents(paths: list[Path]) -> list[Document]:
    documents = []

    for path in paths:
        if not path.exists() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        if path.suffix.lower() == ".pdf":
            documents.extend(load_pdf(path))
        else:
            documents.append(load_text_document(path))

    return documents


def load_pdf(path: Path) -> list[Document]:
    reader = PdfReader(str(path))
    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if not text.strip():
            continue
        documents.append(
            Document(
                text=text,
                metadata={
                    "source": str(path),
                    "title": path.stem,
                    "page": page_number,
                    "document_type": "pdf",
                },
            )
        )

    return documents


def load_text_document(path: Path) -> Document:
    text = path.read_text(encoding="utf-8", errors="ignore")
    suffix = path.suffix.lower().lstrip(".")

    if suffix == "html":
        text = re.sub(r"<[^>]+>", " ", text)
    elif suffix == "json":
        try:
            text = json.dumps(json.loads(text), indent=2)
        except json.JSONDecodeError:
            pass

    return Document(
        text=text,
        metadata={
            "source": str(path),
            "title": path.stem,
            "document_type": suffix,
        },
    )
