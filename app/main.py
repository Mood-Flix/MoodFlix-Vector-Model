# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from model import predict_emotion
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FastAPI Emotion Service")

class EmotionRequest(BaseModel):
    texts: List[str]

@app.post("/emotion")
def analyze(req: EmotionRequest):
    results = []
    for text in req.texts:
        raw_scores = predict_emotion(text)  # list of dicts
        # 출력용으로 소수 둘째자리만 보여주고 합이 1이 되도록 조정(선택)
        probs = [round(item["score"], 2) for item in raw_scores]
        diff = 1.0 - sum(probs)
        probs[-1] += diff  # 마지막에 오차 보정

        scores_display = [
            {"label": item["label"], "score": p}
            for item, p in zip(raw_scores, probs)
        ]
        top_idx = max(range(len(probs)), key=lambda i: probs[i])
        results.append({
            "text": text,
            "emotion_label_idx": top_idx,
            "emotion_label_name": scores_display[top_idx]["label"],
            "scores": scores_display
        })
    return results

@app.get("/health")
def health():
    return {"status": "ok"}