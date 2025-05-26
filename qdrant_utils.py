# qdrant_utils.py
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

def get_qdrant_client(host='localhost', port=6333, api_key=None):
    client = QdrantClient(url=f"http://{host}:{port}", api_key=api_key)
    collection_name = 'trend_terms'
    existing = [c.name for c in client.get_collections().collections]
    if collection_name not in existing:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=768,
                distance=Distance.COSINE
            )
        )
    return client, collection_name
