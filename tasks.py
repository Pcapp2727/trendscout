import os, datetime, requests
from celery_app import app
from data_ingestion import DataIngestion
from trend_clustering import TrendClustering
from qdrant_utils import get_qdrant_client

EXPLODE_KEY = os.getenv('EXPLODING_TOPICS_API_KEY')
REDDIT_CONFIG={'client_id':os.getenv('REDDIT_CLIENT_ID'),'client_secret':os.getenv('REDDIT_CLIENT_SECRET'),'user_agent':os.getenv('REDDIT_USER_AGENT')}
TIKTOK_CONFIG={}
KICK_CONFIG={'base_url':'https://www.kickstarter.com'}
SLACK_WEBHOOK=os.getenv('SLACK_WEBHOOK_URL')

ingestor=DataIngestion(EXPLODE_KEY,REDDIT_CONFIG,TIKTOK_CONFIG,KICK_CONFIG)
client, COLLECTION = get_qdrant_client()
clusterer = TrendClustering(qdrant_client=client)

def notify(msg):
    if SLACK_WEBHOOK: requests.post(SLACK_WEBHOOK,json={'text':msg})

@app.task
def run_ingest_social():
    terms=ingestor.fetch_reddit_new(['r/ZeroWaste','r/DigitalNomad'],limit=50)
    notify(f'Ingested {len(terms)} social terms')

@app.task
def run_ingest_search():
    g=ingestor.fetch_google_trends([''])
    e=ingestor.fetch_exploding_topics(15)
    notify(f'Ingested {len(g)+len(e)} search terms')

@app.task
def run_trends_pipeline():
    # Placeholder: retrieve raw terms
    terms=[]
    stats=[{'term':t,'trend_growth':1,'social_delta':1,'current_volume':1} for t in terms]
    top=clusterer.run_full_pipeline(terms,stats)
    points=[]
    for it in top:
        vec=list(it['sparse'].values)+list(it['dense'])
        pts={'id':f"{it['term']}_{datetime.datetime.utcnow().isoformat()}",'vector':vec,'payload':{'term':it['term'],'momentum':it['momentum'],'cluster':it['cluster']}}
        points.append(pts)
    client.upsert(collection_name=COLLECTION,points=points)
    notify(f'Updated {len(points)} top niches')
