"""Configuração da aplicação, lida de variáveis de ambiente (ou do arquivo .env)."""

import os

from dotenv import load_dotenv

load_dotenv()

# API do Inngest, de onde a UI lê o resultado das runs. Padrão: dev server local.
INNGEST_BASE_URL = os.getenv("INNGEST_BASE_URL", "http://127.0.0.1:8288")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "docs")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
# Precisa bater com o modelo de embedding (bge-m3 = 1024).
EMBED_DIM = int(os.getenv("EMBED_DIM", "1024"))
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:3b")
# Camadas do modelo na GPU. Vazio = Ollama decide; 0 = só CPU (use se a GPU travar o Ollama).
OLLAMA_NUM_GPU = os.getenv("OLLAMA_NUM_GPU") or None
