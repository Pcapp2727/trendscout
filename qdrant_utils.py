# qdrant_utils.py

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

def get_qdrant_client(
    host: str | None = None,
    port: int | None = None,
    url: str | None = None,
    api_key: str | None = None
):
    """
    Initialize a QdrantClient either from a full URL or from host+port.
    """
    if url:
        client = QdrantClient(url=url, api_key=api_key)
    else:
        host = host or "localhost"
        port = port or 6333
        client = QdrantClient(url=f"http://{host}:{port}", api_key=api_key)

    # Ensure the 'trend_terms' collection exists
    collection_name = "trend_terms"
    existing = [c.name for c in client.get_collections().collections]
    if collection_name not in existing:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )

    return client, collection_name

