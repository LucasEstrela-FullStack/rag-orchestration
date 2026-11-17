"""Funções Inngest. Cada chamada externa roda em um step para ter retry e aparecer no painel."""

from pathlib import Path

import inngest

from app import llm, vector_store
from app.ingest import load_and_chunk
from app.inngest_client import inngest_client


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


functions = [ingest_pdf]
