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
cp .env.example .env
```

## Como rodar

Suba o Qdrant:

```bash
docker compose up -d
```

Dashboard do Qdrant: http://localhost:6333/dashboard

Em outro terminal, suba a API que serve as funções do Inngest:

```bash
uv run uvicorn app.main:app --port 8000
```

Em um terceiro terminal, suba o dev server do Inngest (precisa de Node.js):

```bash
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery
```

O painel do Inngest fica em http://127.0.0.1:8288 e mostra cada execução, etapa por etapa.

## Testes

Com o Qdrant rodando:

```bash
uv run pytest
```

## Status

Em construção, passo a passo.
