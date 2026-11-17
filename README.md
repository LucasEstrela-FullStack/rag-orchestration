# rag-orchestration

Pipeline RAG (Retrieval-Augmented Generation) para PDFs. Você envia um PDF, faz perguntas sobre ele e recebe a resposta com as páginas usadas como fonte. A ingestão e a pergunta são funções do Inngest, e cada chamada ao Ollama ou ao Qdrant roda em uma etapa (`step.run`). O Inngest cuida de retries, fila e limites de execução, e mostra no painel o que aconteceu em cada etapa.

Tudo roda na própria máquina: os modelos ficam no Ollama e não há chamada a API paga.

## Stack

| Camada | Tecnologia |
| --- | --- |
| Linguagem | Python 3.12 (gerenciado com [uv](https://docs.astral.sh/uv/)) |
| Orquestração e observabilidade | [Inngest](https://www.inngest.com/) servido por FastAPI |
| Banco vetorial | [Qdrant](https://qdrant.tech/) via Docker |
| Ingestão de PDFs | [LlamaIndex](https://www.llamaindex.ai/) |
| IA (embeddings + LLM) | [Ollama](https://ollama.com/) local: `bge-m3` e `qwen2.5:3b` |
| Interface | [Streamlit](https://streamlit.io/) |

## Como funciona

```text
Streamlit ──evento──> Inngest dev server ──HTTP──> FastAPI (/api/inngest)
    ^                        │                        │
    └── lê o resultado ──────┘                        ├── Ollama (embeddings e LLM)
        (API do Inngest)                              └── Qdrant (vetores)
```

Na ingestão, a interface salva o PDF em `uploads/` e envia o evento `rag/ingest_pdf`. A função lê o PDF página por página, divide o texto em trechos de até 512 tokens (`load-and-chunk`), gera os embeddings e grava tudo no Qdrant (`embed-and-upsert`). O ID de cada ponto vem do arquivo e da posição do trecho, então reenviar o mesmo PDF sobrescreve os trechos em vez de duplicar. Se a nova versão do arquivo tiver menos trechos, os pontos excedentes da versão antiga continuam na coleção.

Na pergunta, a interface envia `rag/query_pdf` com a pergunta e o top-k. A função gera o embedding da pergunta (`embed-query`), busca os trechos mais próximos no Qdrant que passam da similaridade mínima (`search`) e pede a resposta ao LLM com esses trechos como contexto (`answer`). A interface espera a execução terminar e mostra a resposta e as fontes (arquivo e página).

A interface não importa as funções. Ela só envia eventos e lê o resultado pela API do Inngest, então a API e a UI podem rodar em processos separados.

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker
- Node.js, para o dev server do Inngest
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

São quatro processos. Suba o Qdrant:

```bash
docker compose up -d
```

O dashboard do Qdrant fica em http://localhost:6333/dashboard.

Em outro terminal, suba a API que serve as funções do Inngest:

```bash
uv run uvicorn app.main:app --port 8000
```

Em um terceiro terminal, suba o dev server do Inngest:

```bash
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery
```

Atrás de um proxy que intercepta TLS, o `npx` pode falhar ao baixar o pacote. Nesse caso, rode com `NODE_OPTIONS=--use-system-ca`.

O painel do Inngest fica em http://127.0.0.1:8288 e mostra cada execução, etapa por etapa.

Por fim, suba a interface:

```bash
uv run streamlit run streamlit_app.py
```

Ela abre em http://localhost:8501. Envie um PDF, espere a ingestão terminar no painel do Inngest e faça a pergunta.

## Configuração

As variáveis ficam no `.env` (modelo em [.env.example](.env.example)):

| Variável | Padrão | Uso |
| --- | --- | --- |
| `INNGEST_DEV` | sem padrão no código; `1` no `.env.example` | Com `1`, o SDK usa o dev server local do Inngest |
| `INNGEST_BASE_URL` | `http://127.0.0.1:8288` | API do Inngest de onde a UI lê o resultado das execuções |
| `QDRANT_URL` | `http://localhost:6333` | Endereço do Qdrant |
| `QDRANT_COLLECTION` | `docs` | Coleção onde ficam os trechos |
| `MIN_SCORE` | `0.3` | Similaridade mínima de um trecho para entrar no contexto; `0` desliga |
| `OLLAMA_HOST` | `http://localhost:11434` | Endereço do Ollama |
| `EMBED_MODEL` | `bge-m3` | Modelo de embedding |
| `EMBED_DIM` | `1024` | Dimensão do embedding; precisa bater com o modelo |
| `LLM_MODEL` | `qwen2.5:3b` | Modelo que gera a resposta |
| `OLLAMA_NUM_GPU` | vazio | Camadas na GPU. Vazio é automático; `0` força só CPU |

Se o Ollama cair ao gerar embeddings em uma GPU antiga, use `OLLAMA_NUM_GPU=0`.

## Robustez

As duas funções do Inngest ficam em [app/functions.py](app/functions.py). Cada chamada ao Ollama ou ao Qdrant roda em uma etapa (`step.run`). Se uma etapa falhar, só ela é repetida, até 3 vezes, e as etapas já concluídas não rodam de novo. Entradas inválidas, como um caminho de PDF inexistente ou um top-k fora de 1 a 20, falham na hora, sem retry.

A ingestão (`rag/ingest_pdf`) processa um PDF por vez e começa no máximo 2 por minuto. Os PDFs que passam desse ritmo esperam na fila. Se o mesmo arquivo for reenviado em menos de 5 minutos, o evento é ignorado.

A pergunta (`rag/query_pdf`) atende até 2 ao mesmo tempo e é cancelada se passar de 10 minutos.

Para ver o retry funcionando, pare o Qdrant (`docker compose stop qdrant`), faça uma pergunta e religue o Qdrant (`docker compose start qdrant`). A execução fica pendente no painel e termina sozinha se o banco voltar antes de acabarem os 3 retries. Se não voltar, ela termina como `Failed`, e a interface mostra o erro.

## Estrutura

```text
app/
  config.py          variáveis de ambiente
  inngest_client.py  cliente Inngest usado pela API e pela UI
  functions.py       funções de ingestão e de pergunta
  main.py            FastAPI que expõe as funções em /api/inngest
  ingest.py          leitura e chunking do PDF
  llm.py             embedding e chat no Ollama
  prompt.py          montagem das mensagens para o LLM
  vector_store.py    coleção, upsert e busca no Qdrant
streamlit_app.py     interface
tests/               testes com pytest
```

## Testes

Com o Qdrant rodando:

```bash
uv run pytest
```

Os testes do Qdrant usam uma coleção temporária (`test_vector_store`) e não mexem na coleção `docs`.

## Similaridade mínima

A busca só usa trechos com similaridade de cosseno a partir de `MIN_SCORE` (padrão `0.3`). Se nenhum trecho chegar lá, a função responde que não encontrou nada nos documentos, sem fontes e sem chamar o LLM.

O valor veio de um teste pequeno com o `bge-m3` e um único PDF. Perguntas sobre o conteúdo tiveram o melhor trecho entre 0,35 e 0,70. Perguntas sem relação ficaram entre 0,23 e 0,34. Perguntas genéricas como "Sobre o que é o documento?" ficam perto do limite, por isso o padrão é baixo: prefere deixar passar uma pergunta fora do assunto, que o LLM ainda recusa pelo prompt, a descartar uma pergunta válida. Se trocar o modelo de embedding, meça de novo.
