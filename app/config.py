"""Configuração da aplicação, lida de variáveis de ambiente (ou do arquivo .env)."""

import os

from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "docs")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:3b")
# Camadas do modelo na GPU. Vazio = Ollama decide; 0 = só CPU (use se a GPU travar o Ollama).
OLLAMA_NUM_GPU = os.getenv("OLLAMA_NUM_GPU") or None
