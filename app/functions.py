"""Funções Inngest. Cada chamada externa roda em um step para ter retry e aparecer no painel."""

from pathlib import Path

import inngest

from app import llm, vector_store
from app.ingest import load_and_chunk
from app.inngest_client import inngest_client
from app.prompt import build_messages


def _embed_and_upsert(chunks: list[dict]) -> int:
    vectors = llm.embed([chunk["text"] for chunk in chunks])
    ids = [vector_store.point_id(chunk["source"], i) for i, chunk in enumerate(chunks)]
    vector_store.upsert(ids, vectors, chunks)
    return len(chunks)


@inngest_client.create_function(
    fn_id="ingest-pdf",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf"),
)
def ingest_pdf(ctx: inngest.ContextSync) -> dict:
    pdf_path = ctx.event.data.get("pdf_path")
    if not isinstance(pdf_path, str) or not Path(pdf_path).is_file():
        raise inngest.NonRetriableError(f"PDF não encontrado: {pdf_path!r}")

    # shortcut: os chunks trafegam como saída de step (limite de alguns MB); PDFs enormes pediriam lotes.
    chunks = ctx.step.run("load-and-chunk", load_and_chunk, pdf_path)
    stored = ctx.step.run("embed-and-upsert", _embed_and_upsert, chunks)
    return {"source": Path(pdf_path).name, "chunks": stored}


def _embed_query(question: str) -> list[float]:
    return llm.embed([question])[0]


def _answer(question: str, chunks: list[dict]) -> str:
    return llm.chat(build_messages(question, chunks))


@inngest_client.create_function(
    fn_id="query-pdf",
    trigger=inngest.TriggerEvent(event="rag/query_pdf"),
)
def query_pdf(ctx: inngest.ContextSync) -> dict:
    question = ctx.event.data.get("question")
    top_k = ctx.event.data.get("top_k", 5)
    if not isinstance(question, str) or not question.strip():
        raise inngest.NonRetriableError("Pergunta vazia.")
    if not isinstance(top_k, int) or not 1 <= top_k <= 20:
        raise inngest.NonRetriableError(f"top_k deve ser inteiro entre 1 e 20, veio {top_k!r}.")

    vector = ctx.step.run("embed-query", _embed_query, question)
    chunks = ctx.step.run("search", vector_store.search, vector, top_k)
    if not chunks:
        return {"answer": "Nenhum documento indexado ainda. Envie um PDF primeiro.", "sources": []}

    answer = ctx.step.run("answer", _answer, question, chunks)
    sources = sorted({f"{c['source']} (p. {c['page']})" for c in chunks})
    return {"answer": answer, "sources": sources}


functions = [ingest_pdf, query_pdf]
