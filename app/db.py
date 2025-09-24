# app/db.py
import os, re
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

def parse_jdbc_mysql_url(jdbc_url: str):
    m = re.match(r"jdbc:mysql://([^/:]+)(?::(\d+))?/([^?]+)\??(.*)?", jdbc_url)
    if not m:
        raise ValueError(f"Invalid JDBC URL: {jdbc_url}")
    host = m.group(1)
    port = int(m.group(2) or 3306)
    db   = m.group(3)
    q    = m.group(4) or ""
    params = {}
    if q:
        for kv in q.split("&"):
            if "=" in kv:
                k, v = kv.split("=", 1)
                params[k] = v
    return host, port, db, params

def get_engine() -> Engine:
    jdbc_url = os.getenv("DB_URL")
    user = os.getenv("DB_USERNAME")
    pwd  = os.getenv("DB_PASSWORD")
    if not (jdbc_url and user and pwd):
        raise RuntimeError("DB_URL/DB_USERNAME/DB_PASSWORD 환경변수를 설정하세요.")

    host, port, db, params = parse_jdbc_mysql_url(jdbc_url)
    sa_url = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4"

    connect_args = {}
    if str(params.get("ssl-mode", "")).upper() == "REQUIRED":
        # 운영에선 CA 파일 권장: {"ssl":{"ca":"/path/ca.pem"}}
        connect_args = {"ssl": {}}

    eng = create_engine(sa_url, pool_pre_ping=True, connect_args=connect_args)
    return eng
