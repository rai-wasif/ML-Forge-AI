from app.core.config import get_settings
from app.rag.config import DEFAULT_COLLECTION
from app.rag.retriever.retriever import retrieve


def answer_question(question: str, collection_name: str = DEFAULT_COLLECTION, top_k: int = 5) -> dict:
    sources = retrieve(question, collection_name, top_k)
    answer = generate_answer(question, sources)

    return {
        "question": question,
        "answer": answer,
        "collection": collection_name,
        "sources": sources,
    }


def generate_answer(question: str, sources: list[dict]) -> str:
    context = "\n\n".join(f"Source: {item['title']}\n{item['text']}" for item in sources)
    settings = get_settings()

    if settings.groq_api_key:
        try:
            from groq import Groq

            client = Groq(api_key=settings.groq_api_key)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                temperature=0.1,
                messages=[
                    {
                        "role": "system",
                        "content": "Answer only from the provided context. Mention uncertainty when context is weak.",
                    },
                    {
                        "role": "user",
                        "content": f"Question: {question}\n\nContext:\n{context}",
                    },
                ],
            )
            return response.choices[0].message.content
        except Exception:
            pass

    if not sources:
        return "I could not find relevant knowledge-base context for that question."

    snippets = " ".join(item["text"].strip().replace("\n", " ")[:350] for item in sources[:3])
    return f"Based on the indexed knowledge base: {snippets}"
