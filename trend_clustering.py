from fastembed import SparseTextEmbedding
from adaptixx.memory import HybridMemoryRetrievalCore
import numpy as np
from sklearn.cluster import AgglomerativeClustering

class TrendClustering:
    def __init__(self, qdrant_client, dense_embedder_name='openai/text-embedding-ada-002'):
        self.hybrid = HybridMemoryRetrievalCore(
            sparse_model='Qdrant/minicoil-v1',
            dense_model=dense_embedder_name,
            qdrant_client=qdrant_client
        )

    def embed_terms(self, terms):
        sparse_embs = list(self.hybrid.sparse.embed(terms))
        dense_embs = list(self.hybrid.dense.embed(terms))
        return [{'term': t, 'sparse': s, 'dense': d} for t, s, d in zip(terms, sparse_embs, dense_embs)]

    def cluster_terms(self, embedded_terms, n_clusters=20):
        vectors = []
        for e in embedded_terms:
            sv = np.zeros(max(e['sparse'].indices)+1, dtype=np.float32)
            sv[e['sparse'].indices] = e['sparse'].values
            dv = np.array(e['dense'])
            vectors.append(np.concatenate([sv, dv]))
        X = np.vstack(vectors)
        labels = AgglomerativeClustering(n_clusters=n_clusters).fit_predict(X)
        for e, lbl in zip(embedded_terms, labels):
            e['cluster'] = int(lbl)
        return embedded_terms

    def score_momentum(self, stats):
        eps = 1e-6
        for item in stats:
            g = item.get('trend_growth', 0)
            s = item.get('social_delta', 0)
            v = item.get('current_volume', 1)
            item['momentum'] = (g * s) / (v + eps)
        return stats

    def run_full_pipeline(self, terms, stats, n_clusters=20):
        embedded = self.embed_terms(terms)
        clustered = self.cluster_terms(embedded, n_clusters)
        stats_map = {s['term']: s for s in stats}
        for e in clustered:
            e.update(stats_map.get(e['term'], {}))
        scored = self.score_momentum(clustered)
        output = []
        for lbl in set(e['cluster'] for e in scored):
            cluster_items = [e for e in scored if e['cluster'] == lbl]
            top = sorted(cluster_items, key=lambda x: x['momentum'], reverse=True)[0]
            output.append(top)
        return output
