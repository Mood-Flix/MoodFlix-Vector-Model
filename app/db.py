# app/db.py
import os, re
from urllib.parse import quote_plus
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

    sa_url = URL.create(
            drivername="mysql+pymysql",
            username=user,
            password=pwd,
            host=host,
            port=int(port) if port else None,
            database=db,
            query=query,
        )

    connect_args = {}
        ssl_mode = str(params.get("ssl-mode", "")).upper() if params else ""
        if ssl_mode == "REQUIRED":
            ca_path = os.getenv("DB_SSL_CA")  # 선택
            if ca_path:
                connect_args = {"ssl": {"ca": ca_path}}
            else:
                # 최소한의 SSL 활성화 (PyMySQL는 빈 dict도 SSL 사용으로 간주)
                connect_args = {"ssl": {}}

      engine = create_engine(
            sa_url,
            pool_pre_ping=True,   # 죽은 커넥션 자동 감지
            pool_recycle=1800,    # 30분마다 재연결 (Cloud SQL/Aiven 등 idle timeout 대응)
            pool_size=5,
            max_overflow=10,
            connect_args=connect_args,
        )
        return engine
