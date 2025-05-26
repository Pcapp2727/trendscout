import time
from pytrends.request import TrendReq
import requests
import praw
from bs4 import BeautifulSoup

class DataIngestion:
    def __init__(self, exploding_topics_api_key, reddit_config, tiktok_config, kickstarter_config):
        self.pytrends = TrendReq()
        self.et_api_key = exploding_topics_api_key
        self.reddit = praw.Reddit(**reddit_config)
        self.tiktok_config = tiktok_config
        self.kickstarter_base = kickstarter_config['base_url']

    def fetch_google_trends(self, kw_list, timeframe='now 7-d'):
        self.pytrends.build_payload(kw_list, timeframe=timeframe)
        data = self.pytrends.trending_searches(pn='united_states')
        return data.tolist()

    def fetch_exploding_topics(self, min_growth=10):
        url = 'https://api.explodingtopics.com/v1/topics'
        headers = {'Authorization': f'Bearer {self.et_api_key}'}
        params = {'growth_min': min_growth}
        resp = requests.get(url, headers=headers, params=params).json()
        return [t['name'] for t in resp['data']]

    def fetch_reddit_new(self, subreddits, limit=100):
        posts = []
        for sub in subreddits:
            for post in self.reddit.subreddit(sub).new(limit=limit):
                posts.append(post.title)
            time.sleep(1)
        return posts

    def fetch_tiktok_trends(self):
        raise NotImplementedError

    def fetch_kickstarter(self, category, max_pages=5):
        results = []
        for page in range(1, max_pages+1):
            url = f'{self.kickstarter_base}/discover/advanced?category_id={category}&page={page}'
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'html.parser')
            for card in soup.select('.js-react-proj-card'):
                title = card.select_one('.project-title').text.strip()
                results.append(title)
            time.sleep(2)
        return results
