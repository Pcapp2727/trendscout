from celery import Celery

app = Celery('trend_tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/1')
app.conf.beat_schedule = {
    'ingest-social-hourly': {'task': 'tasks.run_ingest_social', 'schedule': 3600},
    'ingest-search-twice-daily': {'task': 'tasks.run_ingest_search', 'schedule': {'type':'crontab','hour':[0,12],'minute':15}},
    'pipeline-nightly': {'task': 'tasks.run_trends_pipeline', 'schedule': {'type':'crontab','hour':2,'minute':30}},
}
app.conf.timezone='America/New_York'
