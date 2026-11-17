"""Montagem do prompt de RAG a partir da pergunta e dos chunks encontrados."""

SYSTEM = (
    "Você responde perguntas sobre documentos usando apenas o contexto fornecido. "
    "Se o contexto não tiver a resposta, diga que não encontrou a informação nos documentos. "
    "Responda em português, de forma direta."
)


def build_messages(question: str, chunks: list[dict]) -> list[dict[str, str]]:
    context = "\n\n".join(f"[{c['source']}, p. {c['page']}]\n{c['text']}" for c in chunks)
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Contexto:\n\n{context}\n\nPergunta: {question}"},
    ]
