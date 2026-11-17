from pathlib import Path

from app.ingest import load_and_chunk


def write_pdf(path: Path, pages: list[str]) -> None:
    """Gera um PDF mínimo com um texto por página, sem dependências extras."""
    objects = ["<< /Type /Catalog /Pages 2 0 R >>", ""]
    kids = []
    for text in pages:
        content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
        page_num, content_num = len(objects) + 1, len(objects) + 2
        kids.append(f"{page_num} 0 R")
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {content_num} 0 R "
            "/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>"
        )
        objects.append(f"<< /Length {len(content)} >>\nstream\n{content.decode()}\nendstream")
    objects[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(pages)} >>"

    out, offsets = b"%PDF-1.4\n", []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n{obj}\nendobj\n".encode()
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    out += "".join(f"{o:010d} 00000 n \n" for o in offsets).encode()
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    path.write_bytes(out)


def test_load_and_chunk_keeps_source_and_page(tmp_path: Path):
    pdf = tmp_path / "manual.pdf"
    write_pdf(pdf, ["Primeira pagina sobre Qdrant", "Segunda pagina sobre Inngest"])

    chunks = load_and_chunk(pdf)

    assert [c["page"] for c in chunks] == ["1", "2"]
    assert all(c["source"] == "manual.pdf" for c in chunks)
    assert "Qdrant" in chunks[0]["text"]
    assert "Inngest" in chunks[1]["text"]


def test_long_page_is_split_into_several_chunks(tmp_path: Path):
    pdf = tmp_path / "longo.pdf"
    write_pdf(pdf, ["palavra " * 2000])

    chunks = load_and_chunk(pdf)

    assert len(chunks) > 1
    assert all(c["page"] == "1" for c in chunks)
