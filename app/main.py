# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .vectorize import LABELS, vectorize_text, model_version
from .embed_runner import run_embedding_batch, query_topn_by_vector, count_vectors

app = FastAPI(title="MoodFlix Vector Service")

@app.get("/health")
def health():
    return {"status": "ok", "vectors": count_vectors()}

@app.get("/labels")
def labels():
    return {"labels": LABELS, "version": model_version()}

class VectorizeTextRequest(BaseModel):
    text: str
    translate_to_ko: bool = False

class VectorizeTextResponse(BaseModel):
    labels: List[str]
    vector: List[float]
    version: str

@app.post("/vectorize/text", response_model=VectorizeTextResponse)
def vectorize(req: VectorizeTextRequest):
    try:
        vec = vectorize_text(req.text)
        return {"labels": LABELS, "vector": vec, "version": model_version()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/embedding/run")
def admin_run_embedding(chunk: int = 200):
    res = run_embedding_batch(chunk=chunk)
    return {"status": "ok", "result": res}

class RecommendItem(BaseModel):
    movie_id: int
    title: Optional[str] = None
    genres: List[str] = []
    similarity: float

class RecommendResponse(BaseModel):
    version: str
    items: List[RecommendItem]

@app.get("/recommend/by-text", response_model=RecommendResponse)
def recommend_by_text(text: str, topN: int = 20):
    q = vectorize_text(text)
    items = query_topn_by_vector(q, topn=topN)
    return {"version": model_version(), "items": [RecommendItem(**it) for it in items]}
