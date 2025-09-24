FROM python:3.10-slim

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    HF_HOME=/opt/hf-cache \
    TRANSFORMERS_CACHE=/opt/hf-cache \
    HF_HUB_ENABLE_HF_TRANSFER=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 먼저 설치(캐시 최대화)
COPY app/requirements.txt .
RUN pip install --no-cache-dir --retries 5 --timeout 120 -r requirements.txt

# 앱 복사
COPY app/ /app/app/

EXPOSE 8081
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8001","--timeout-keep-alive","75"]
