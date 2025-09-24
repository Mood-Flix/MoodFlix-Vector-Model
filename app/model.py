from transformers import pipeline
import math
import threading

# 파이프라인은 lazy-load + 싱글톤
_pipe = None
_lock = threading.Lock()

def get_pipe():
    global _pipe
    if _pipe is None:
        with _lock:
            if _pipe is None:
                _pipe = pipeline(
                    "text-classification",
                    model="searle-j/kote_for_easygoing_people",
                    tokenizer="searle-j/kote_for_easygoing_people",
                    return_all_scores=True,
                    device=-1,  # GPU면 0
                )
    return _pipe

def _label_order():
    p = get_pipe()
    id2 = getattr(p.model.config, "id2label", None)
    if id2:
        return [id2[i] for i in sorted(id2.keys())]
    return [x["label"] for x in p("warmup")[0]]

LABELS = _label_order()

def _l2(v):
    s = sum(x*x for x in v)
    return [x/(s**0.5) for x in v] if s > 0 else v

def vectorize_text(text: str):
    p = get_pipe()
    raw = p(text)[0]  # [{"label","score"}, ...]
    m = {d["label"]: float(d["score"]) for d in raw}
    vec = [m.get(lbl, 0.0) for lbl in LABELS]
    return _l2(vec)

def model_version() -> str:
    p = get_pipe()
    return str(getattr(p.model.config, "name_or_path", "unknown"))
