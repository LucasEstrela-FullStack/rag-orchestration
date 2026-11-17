"""Cliente Inngest compartilhado pela API (que serve as funções) e pela UI (que envia eventos)."""

import logging

import inngest

from app import config  # noqa: F401  carrega o .env antes do cliente ler INNGEST_DEV

inngest_client = inngest.Inngest(app_id="rag-orchestration", logger=logging.getLogger("uvicorn"))
