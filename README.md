# rag-orchestration

Pipeline RAG (Retrieval-Augmented Generation) para PDFs, construído com práticas de produção: orquestração, observabilidade, retries, throttling e controle de concorrência.

## Stack

| Camada | Tecnologia |
| --- | --- |
| Linguagem | Python 3.12 (gerenciado com [uv](https://docs.astral.sh/uv/)) |
| Orquestração e observabilidade | [Inngest](https://www.inngest.com/) |
| Banco vetorial | [Qdrant](https://qdrant.tech/) via Docker |
| Ingestão de PDFs | [LlamaIndex](https://www.llamaindex.ai/) |
| IA (embeddings + LLM) | [Ollama](https://ollama.com/) local: `bge-m3` e `qwen2.5:3b` |
| Interface | [Streamlit](https://streamlit.io/) |

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker
- Ollama com os modelos:

```bash
ollama pull bge-m3
ollama pull qwen2.5:3b
```

## Instalação

```bash
uv sync
```

## Status

Em construção, passo a passo. Veja [context/progress-tracker.md](context/progress-tracker.md).
