"""Chamadas ao Ollama: embeddings e chat."""

from ollama import Client

from app import config

_client = Client(host=config.OLLAMA_HOST)
_options = {"num_gpu": int(config.OLLAMA_NUM_GPU)} if config.OLLAMA_NUM_GPU else None


def embed(texts: list[str]) -> list[list[float]]:
    """Gera um vetor por texto, na mesma ordem."""
    response = _client.embed(model=config.EMBED_MODEL, input=texts, options=_options)
    return [list(vector) for vector in response.embeddings]


def chat(messages: list[dict[str, str]]) -> str:
    """Envia mensagens no formato {"role", "content"} e devolve o texto da resposta."""
    response = _client.chat(model=config.LLM_MODEL, messages=messages, options=_options)
    return response.message.content or ""
