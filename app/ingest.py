"""Leitura de PDF e divisão do texto em chunks com LlamaIndex."""

from pathlib import Path

from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.file import PDFReader

# Tamanho em tokens. Chunks menores = busca mais precisa; sobreposição evita cortar ideias no meio.
_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)


def load_and_chunk(path: str | Path) -> list[dict]:
    """Lê o PDF página a página e devolve chunks com texto, arquivo e página de origem."""
    path = Path(path)
    chunks = []
    for document in PDFReader().load_data(file=path):
        page = document.metadata.get("page_label")
        for text in _splitter.split_text(document.text):
            chunks.append({"text": text, "source": path.name, "page": page})
    return chunks
