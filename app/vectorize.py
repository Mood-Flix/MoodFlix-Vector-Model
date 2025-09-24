from transformers import pipeline
import threading
from typing import List

_PIPE = None
_LOCK = threading.Lock()

def get_pipe():
    global _PIPE
    if _PIPE is None:
        with _LOCK:
            if _PIPE is None:
                _PIPE = pipeline(
                    "text-classification",
                    model="searle-j/kote_for_easygoing_people",
                    tokenizer="searle-j/kote_for_easygoing_people",
                    # return_all_scores=True,  # ← deprecated
                    top_k=None,               # ← 전체 라벨 점수 반환
                    device=-1,                # GPU면 0
                )
    return _PIPE

def _label_order(p) -> List[str]:
    id2 = getattr(p.model.config, "id2label", None)
    return [id2[i] for i in sorted(id2.keys())] if id2 else [x["label"] for x in p("warmup", truncation=True)[0]]

def _safe_text(text: str, max_chars: int = 5000) -> str:
    """아주 긴 텍스트가 들어와도 과도한 메모리/시간을 막기 위해 하드 컷."""
    if not text:
        return ""
    return text[:max_chars]

# 초기 라벨 고정
LABELS: List[str] = _label_order(get_pipe())

def _l2(v: List[float]) -> List[float]:
    s = sum(x*x for x in v)
    return [x/(s**0.5) for x in v] if s > 0 else v

def vectorize_text(text: str) -> List[float]:
    p = get_pipe()
    # ★ 핵심: truncation=True 로 512 토큰 이내로 절단
    raw = p(_safe_text(text), truncation=True)[0]  # [{"label","score"}, ...]
    m = {d["label"]: float(d["score"]) for d in raw}
    vec = [m.get(lbl, 0.0) for lbl in LABELS]
    return _l2(vec)

def vectorize_movie(overview: str, genres: List[str], keywords: List[str], reviews: List[str],
                    weights=(0.60, 0.15, 0.15, 0.10)) -> List[float]:
    fields = [
        _safe_text(overview or ""),
        _safe_text(" ".join(genres or [])),
        _safe_text(" ".join(keywords or [])),
        _safe_text(" ".join(reviews or "")),
    ]
    acc = [0.0] * len(LABELS)
    for txt, w in zip(fields, list(weights)[:4]):
        if not txt or w <= 0:
            continue
        v = vectorize_text(txt)  # 내부에서 truncation 적용됨
        for i in range(len(acc)):
            acc[i] += w * v[i]
    return _l2(acc)

def model_version() -> str:
    return str(get_pipe().model.config.name_or_path)
