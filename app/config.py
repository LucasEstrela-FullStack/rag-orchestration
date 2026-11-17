"""Configuração da aplicação, lida de variáveis de ambiente (ou do arquivo .env)."""

import os

from dotenv import load_dotenv

load_dotenv()

# API do Inngest, de onde a UI lê o resultado das runs. Padrão: dev server local.
INNGEST_BASE_URL = os.getenv("INNGEST_BASE_URL", "http://127.0.0.1:8288")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "docs")
# Similaridade mínima (cosseno) de um trecho para entrar no contexto. Calibrado com bge-m3: perguntas
# relevantes ficaram de 0.35 a 0.70, fora do assunto de 0.23 a 0.34. 0 desliga o filtro.
MIN_SCORE = float(os.getenv("MIN_SCORE") or "0.3")
if not 0 <= MIN_SCORE <= 1:  # também barra nan e inf
    raise ValueError(f"MIN_SCORE deve estar entre 0 e 1, veio {MIN_SCORE}.")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
# Precisa bater com o modelo de embedding (bge-m3 = 1024).
EMBED_DIM = int(os.getenv("EMBED_DIM", "1024"))
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:3b")
# Camadas do modelo na GPU. Vazio = Ollama decide; 0 = só CPU (use se a GPU travar o Ollama).
OLLAMA_NUM_GPU = os.getenv("OLLAMA_NUM_GPU") or None
