# cluster.py

import os
import datetime
from trend_clustering import TrendClustering
from qdrant_utils import get_qdrant_client
from qdrant_client.http.exceptions import ResponseHandlingException

# Load secrets
QDRANT_URL     = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Init Qdrant + clustering
try:
    client, COLLECTION = get_qdrant_client(url=QDRANT_URL, api_key=QDRANT_API_KEY)
except ResponseHandlingException:
    print("ERROR: Cannot connect to Qdrant.")
    exit(1)

clusterer = TrendClustering(qdrant_client=client)

# Fetch raw terms back from payloads
# (We stored them with id="raw_{term}" above)
scroll = client.scroll(collection_name=COLLECTION, with_payload=True, limit=1000)
terms = [pt.payload["raw_term"] for pt in scroll if pt.payload.get("raw_term")]

# Build placeholder stats: you can enrich these with real metrics later
stats = [{"term": t, "trend_growth": 1.0, "social_delta": 1.0, "current_volume": 1.0} for t in terms]

# Run clustering & scoring
top = clusterer.run_full_pipeline(terms, stats, n_clusters=20)

# Upsert top clusters with real vectors + payload
points = []
for item in top:
    vec = list(item["sparse"].values) + list(item["dense"])
    points.append({
        "id": f"top_{item['term']}_{datetime.datetime.utcnow().isoformat()}",
        "vector": vec,
        "payload": {
            "term": item["term"],
            "momentum": item["momentum"],
            "cluster": item["cluster"]
        }
    })

client.upsert(collection_name=COLLECTION, points=points)
print(f"Upserted {len(points)} top clusters.")
