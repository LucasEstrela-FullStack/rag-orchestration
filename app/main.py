"""API que expõe as funções Inngest em /api/inngest."""

import inngest.fast_api
from fastapi import FastAPI

from app.functions import functions
from app.inngest_client import inngest_client

app = FastAPI(title="rag-orchestration")
inngest.fast_api.serve(app, inngest_client, functions)
