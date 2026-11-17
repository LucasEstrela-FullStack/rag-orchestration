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

## Robustez

As duas funções do Inngest ficam em [app/functions.py](app/functions.py). Cada chamada ao Ollama ou ao Qdrant roda em uma etapa (`step.run`). Se uma etapa falhar, só ela é repetida, até 3 vezes, e as etapas já concluídas não rodam de novo.

A ingestão (`rag/ingest_pdf`) processa um PDF por vez e começa no máximo 2 por minuto. Os PDFs que passam desse ritmo esperam na fila. Se o mesmo arquivo for reenviado em menos de 5 minutos, o evento é ignorado.

A pergunta (`rag/query_pdf`) atende até 2 ao mesmo tempo e é cancelada se passar de 10 minutos.

Para ver o retry funcionando, pare o Qdrant (`docker compose stop qdrant`), faça uma pergunta e religue o Qdrant (`docker compose start qdrant`). A execução fica pendente no painel e termina sozinha quando o banco volta.

## Testes

Com o Qdrant rodando:

```bash
uv run pytest
```

## Status

Em construção, passo a passo.
