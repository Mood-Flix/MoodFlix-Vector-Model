from transformers import pipeline
import math
import threading
from typing import List, Optional

# ---- Lazy singleton pipeline ----
_PIPE = None
_LOCK = threading.Lock()
_LABELS: List[str] = []  # import 시 모델/라벨 미로딩

def _label_order(clf) -> List[str]:
    id2 = getattr(clf.model.config, "id2label", None)
    if isinstance(id2, dict) and id2:
        return [id2[i] for i in sorted(id2.keys())]
    # id2label이 없을 경우 대비(드물지만)
    return [str(i) for i in range(len(clf("테스트")[0]))]

def get_pipe():
    """최초 호출 시에만 모델 로딩(콜드스타트 지연 방지)."""
    global _PIPE, _LABELS
    if _PIPE is None:
        with _LOCK:
            if _PIPE is None:
                _PIPE = pipeline(
                    "text-classification",
                    model="searle-j/kote_for_easygoing_people",
                    tokenizer="searle-j/kote_for_easygoing_people",
                    top_k=None,   # ← return_all_scores=True 대체
                    device=-1,    # GPU면 0
                )
                if not _LABELS:
                    _LABELS = _label_order(_PIPE)
    return _PIPE

def ensure_labels() -> List[str]:
    """라벨이 필요할 때만 로딩."""
    global _LABELS
    if not _LABELS:
        _ = get_pipe()
    return _LABELS

def _l2(vec: List[float]) -> List[float]:
    s = sum(x * x for x in vec)
    if s <= 0.0:
        return vec
    n = math.sqrt(s)
    return [x / n for x in vec]

def vectorize_text(text: str) -> List[float]:
    """입력 문장을 43차 감정 벡터(L2 정규화)로 변환."""
    p = get_pipe()
    labels = ensure_labels()
    raw = p(text)[0]  # [{ "label": ..., "score": ...}, ...]
    label2score = {d["label"]: float(d["score"]) for d in raw}
    vec = [label2score.get(lbl, 0.0) for lbl in labels]
    return _l2(vec)

def model_version() -> str:
    p = get_pipe()
    # name_or_path가 없을 때의 안전한 폴백
    return str(getattr(p.model.config, "name_or_path", getattr(p.model, "__class__", type("M", (), {})).__name__))
