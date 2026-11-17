"""Interface Streamlit: envia PDFs para ingestão e faz perguntas, tudo via eventos do Inngest."""

import json
import time
import urllib.request
from pathlib import Path

import inngest
import streamlit as st

from app.config import INNGEST_BASE_URL
from app.inngest_client import inngest_client

UPLOAD_DIR = Path(__file__).parent / "uploads"
FINISHED = {"Completed", "Failed", "Cancelled"}


def _get(path: str) -> dict:
    with urllib.request.urlopen(f"{INNGEST_BASE_URL}{path}", timeout=10) as resp:
        return json.load(resp)


def wait_for_run(event_id: str, timeout_s: float = 600) -> dict:
    """Espera a run disparada pelo evento terminar e devolve o detalhe dela."""
    deadline = time.monotonic() + timeout_s
    run_id = None
    while time.monotonic() < deadline:
        if run_id is None:
            runs = _get(f"/v1/events/{event_id}/runs").get("data") or []
            run_id = runs[0]["run_id"] if runs else None
        # A lista de runs marca Completed antes do detalhe ter o output; por isso o status vem daqui.
        if run_id is not None:
            run = _get(f"/v1/runs/{run_id}")["data"]
            if run["status"] in FINISHED:
                return run
        time.sleep(1)
    raise TimeoutError("A run não terminou a tempo.")


st.set_page_config(page_title="RAG com Inngest", page_icon="📄")
st.title("Pergunte aos seus PDFs")

st.header("Enviar PDF")
uploaded = st.file_uploader("Escolha um PDF", type="pdf")
if uploaded and st.button("Indexar PDF"):
    UPLOAD_DIR.mkdir(exist_ok=True)
    pdf_path = UPLOAD_DIR / Path(uploaded.name).name
    pdf_path.write_bytes(uploaded.getvalue())
    try:
        inngest_client.send_sync(inngest.Event(name="rag/ingest_pdf", data={"pdf_path": str(pdf_path)}))
    except Exception as exc:
        st.error(f"Não foi possível falar com o Inngest. Confira se o dev server está rodando. ({exc})")
    else:
        st.success(f"{pdf_path.name} enviado. A ingestão roda em segundo plano; acompanhe no painel do Inngest.")

st.header("Perguntar")
with st.form("question"):
    question = st.text_input("Sua pergunta")
    top_k = st.number_input("Trechos a buscar (top-k)", min_value=1, max_value=20, value=5)
    submitted = st.form_submit_button("Perguntar")

if submitted:
    if not question.strip():
        st.error("Digite uma pergunta.")
    else:
        try:
            event_id = inngest_client.send_sync(
                inngest.Event(name="rag/query_pdf", data={"question": question, "top_k": int(top_k)})
            )[0]
            with st.spinner("Buscando e gerando a resposta..."):
                run = wait_for_run(event_id)
        except TimeoutError:
            st.error("A resposta demorou demais. Confira o Ollama e o painel do Inngest.")
        except Exception as exc:
            st.error(f"Não foi possível falar com o Inngest. Confira se o dev server está rodando. ({exc})")
        else:
            if run["status"] != "Completed":
                st.error(f"A run terminou como {run['status']}. Veja o erro no painel do Inngest.")
            else:
                st.write(run["output"]["answer"])
                if run["output"]["sources"]:
                    st.caption("Fontes")
                    for source in run["output"]["sources"]:
                        st.markdown(f"- {source}")
