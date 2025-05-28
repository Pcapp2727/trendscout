# ingest.py

import os
from data_ingestion import DataIngestion
from qdrant_utils import get_qdrant_client
from qdrant_client.http.exceptions import ResponseHandlingException

# Load secrets (provided via GitHub Actions secrets)
QDRANT_URL       = os.getenv("QDRANT_URL")
QDRANT_API_KEY   = os.getenv("QDRANT_API_KEY")
EXPLODE_API_KEY  = os.getenv("EXPLODING_TOPICS_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Initialize Qdrant client
try:
    client, COLLECTION = get_qdrant_client(url=QDRANT_URL, api_key=QDRANT_API_KEY)
except ResponseHandlingException:
    print("ERROR: Cannot connect to Qdrant.")
    exit(1)

# Initialize ingestor
ingestor = DataIngestion(
    exploding_topics_api_key=EXPLODE_API_KEY,
    reddit_config={
        "client_id": REDDIT_CLIENT_ID,
        "client_secret": REDDIT_CLIENT_SECRET,
        "user_agent": REDDIT_USER_AGENT
    },
    tiktok_config={},  # add if implemented
    kickstarter_config={"base_url": "https://www.kickstarter.com"}
)

# Fetch raw terms
google_terms    = ingestor.fetch_google_trends([''])
exploding_terms = ingestor.fetch_exploding_topics(min_growth=15)
reddit_terms    = ingestor.fetch_reddit_new(['r/ZeroWaste','r/DigitalNomad'], limit=50)

# Persist raw terms as upserts with a simple payload (optional)
raw = set(google_terms + exploding_terms + reddit_terms)
points = []
for term in raw:
    points.append({
        "id": f"raw_{term}",
        "vector": [],  # no vector, just store payload
        "payload": {"raw_term": term}
    })
# Upsert raw terms (will store payloads; vector empty means no index)
client.upsert(collection_name=COLLECTION, points=points)
print(f"Ingested {len(raw)} raw terms.")
