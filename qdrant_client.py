from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

def get_qdrant_client(host='localhost', port=6333, api_key=None):
    client = QdrantClient(url=f'http://{host}:{port}', api_key=api_key)
    name = 'trend_terms'
    if name not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
    return client, name
