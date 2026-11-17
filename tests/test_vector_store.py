"""Testes de integração: precisam do Qdrant rodando (docker compose up -d)."""

import pytest

from app import config, vector_store

COLLECTION = "test_vector_store"


def one_hot(position: int) -> list[float]:
    vector = [0.0] * config.EMBED_DIM
    vector[position] = 1.0
    return vector


@pytest.fixture
def collection():
    vector_store._client.delete_collection(COLLECTION)
    yield COLLECTION
    vector_store._client.delete_collection(COLLECTION)


def test_point_id_is_deterministic():
    assert vector_store.point_id("a.pdf", 0) == vector_store.point_id("a.pdf", 0)
    assert vector_store.point_id("a.pdf", 0) != vector_store.point_id("a.pdf", 1)
    assert vector_store.point_id("a.pdf", 0) != vector_store.point_id("b.pdf", 0)


def test_search_returns_most_similar_first(collection):
    ids = [vector_store.point_id("a.pdf", i) for i in range(3)]
    payloads = [{"source": "a.pdf", "text": f"chunk {i}"} for i in range(3)]
    vector_store.upsert(ids, [one_hot(i) for i in range(3)], payloads, name=collection)

    hits = vector_store.search(one_hot(1), top_k=2, name=collection)

    assert len(hits) == 2
    assert hits[0]["text"] == "chunk 1"
    assert hits[0]["score"] == pytest.approx(1.0)


def test_upsert_same_ids_does_not_duplicate(collection):
    ids = [vector_store.point_id("a.pdf", i) for i in range(2)]
    vectors = [one_hot(i) for i in range(2)]
    payloads = [{"source": "a.pdf", "text": f"chunk {i}"} for i in range(2)]

    vector_store.upsert(ids, vectors, payloads, name=collection)
    vector_store.upsert(ids, vectors, payloads, name=collection)

    assert vector_store._client.count(collection).count == 2
