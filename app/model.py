# app/model.py
from transformers import pipeline
import torch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEVICE = 0 if torch.cuda.is_available() else -1

logger.info("Loading pipeline...")
# return_all_scores=True or top_k=None: 모든 라벨 점수 반환
pipe = pipeline(
    "text-classification",
    model="searle-j/kote_for_easygoing_people",
    tokenizer="searle-j/kote_for_easygoing_people",
    return_all_scores=True,
    device=DEVICE
)
logger.info("Pipeline loaded.")

# helper: 입력 문장 -> (top_label, scores_list)
def predict_emotion(text: str):
    raw = pipe(text)[0]  # list of {"label":..., "score":...}
    # raw는 pipeline이 준 그대로(소수점 아주 많은 값)
    # 필요하면 rounding/정규화는 호출자(main.py)에서 처리
    return raw