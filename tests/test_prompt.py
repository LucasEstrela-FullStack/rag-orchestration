from app.prompt import build_messages

CHUNKS = [
    {"text": "O Qdrant guarda vetores.", "source": "manual.pdf", "page": "3", "score": 0.9},
    {"text": "O Inngest faz retries.", "source": "guia.pdf", "page": "7", "score": 0.8},
]


def test_user_message_has_question_and_every_chunk_with_its_origin():
    messages = build_messages("O que o Qdrant guarda?", CHUNKS)

    user = messages[-1]
    assert user["role"] == "user"
    assert "O que o Qdrant guarda?" in user["content"]
    assert "[manual.pdf, p. 3]\nO Qdrant guarda vetores." in user["content"]
    assert "[guia.pdf, p. 7]\nO Inngest faz retries." in user["content"]


def test_system_message_limits_answer_to_context():
    system = build_messages("pergunta", CHUNKS)[0]

    assert system["role"] == "system"
    assert "contexto" in system["content"].lower()
