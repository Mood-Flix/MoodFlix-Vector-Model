# app/embed_runner.py
from typing import Dict, Any, List
from .db import get_engine
from .db_fetch import fetch_movies_for_embedding
from .vectorize import vectorize_movie

# 데모: 메모리 보관(운영: ChromaDB upsert로 교체)
_MOVIE_VECS: Dict[int, Dict[str, Any]] = {}

def run_embedding_batch(chunk=200, weights=(0.70,0.10,0.10,0.10), max_pages=None):
    eng = get_engine()
    page, offset, total = 0, 0, 0
    while True:
        rows = fetch_movies_for_embedding(eng, offset, chunk)
        if not rows:
            break
        batch: List[Dict[str, Any]] = []
        for it in rows:
            vec = vectorize_movie(
                overview=it["overview"],
                genres=it["genres"],
                keywords=it["keywords"],
                reviews=it["reviews"],
                weights=weights
            )
            item = {"id": it["id"], "title": it["title"], "genres": it["genres"], "vector": vec}
            _MOVIE_VECS[it["id"]] = item
            batch.append(item)
        total += len(batch); page += 1; offset += chunk
        if max_pages and page >= max_pages:
            break
    return {"pages": page, "upserts": total}

def query_topn_by_vector(qvec, topn=20):
    def dot(a,b): return sum(x*y for x,y in zip(a,b))
    scored = [(dot(qvec, rec["vector"]), mid, rec) for mid, rec in _MOVIE_VECS.items()]
    scored.sort(key=lambda x: x[0], reverse=True)
    out = []
    for sim, mid, rec in scored[:topn]:
        out.append({"movie_id": mid, "title": rec["title"], "genres": rec["genres"], "similarity": sim})
    return out

def count_vectors() -> int:
    return len(_MOVIE_VECS)
