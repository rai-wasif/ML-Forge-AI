from llama_index.core.node_parser import SentenceSplitter


def chunk_documents(documents, chunk_size: int = 800, chunk_overlap: int = 120) -> list[dict]:
    parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    nodes = parser.get_nodes_from_documents(documents)
    chunks = []

    for index, node in enumerate(nodes):
        chunks.append(
            {
                "text": node.get_content(metadata_mode="none"),
                "metadata": {
                    **node.metadata,
                    "chunk_id": index,
                },
            }
        )

    return chunks
