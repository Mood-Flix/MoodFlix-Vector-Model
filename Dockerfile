# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 시스템 deps (필요시 확장)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 복사
COPY app/ /app/

# Uvicorn 실행 (worker=1 권장: 모델 메모리 중복 방지)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]