"""Acesso ao Qdrant: coleção, gravação e busca de chunks."""

import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app import config

_client = QdrantClient(url=config.QDRANT_URL)


def ensure_collection(name: str = config.QDRANT_COLLECTION) -> None:
    """Cria a coleção se ainda não existir."""
    if not _client.collection_exists(name):
        _client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=config.EMBED_DIM, distance=Distance.COSINE),
        )


def point_id(source: str, index: int) -> str:
    """ID determinístico: reprocessar o mesmo arquivo sobrescreve os pontos em vez de duplicar."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source}:{index}"))


def upsert(
    ids: list[str],
    vectors: list[list[float]],
    payloads: list[dict],
    name: str = config.QDRANT_COLLECTION,
) -> None:
    ensure_collection(name)
    points = [
        PointStruct(id=id_, vector=vector, payload=payload)
        for id_, vector, payload in zip(ids, vectors, payloads, strict=True)
    ]
    _client.upsert(collection_name=name, points=points)


def search(
    vector: list[float],
    top_k: int = 5,
    min_score: float | None = None,
    name: str = config.QDRANT_COLLECTION,
) -> list[dict]:
    """Devolve até `top_k` chunks mais similares, com score acima de `min_score`: payload + score."""
    ensure_collection(name)
    result = _client.query_points(
        collection_name=name, query=vector, limit=top_k, score_threshold=min_score or None, with_payload=True
    )
    return [{**(point.payload or {}), "score": point.score} for point in result.points]
