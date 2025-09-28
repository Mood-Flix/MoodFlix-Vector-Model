import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL

# 참고: 이 함수는 더 이상 사용되지 않으므로 추후 삭제 가능합니다.
def parse_jdbc_mysql_url(jdbc_url: str):
    import re
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
    # DB_URL 대신 개별 환경 변수를 직접 사용하도록 변경
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    user = os.getenv("DB_USERNAME")
    pwd  = os.getenv("DB_PASSWORD")
    db   = os.getenv("DB_NAME")

    # 모든 필수 환경 변수가 있는지 확인
    if not all([host, port, user, pwd, db]):
        raise RuntimeError("DB_HOST/DB_PORT/DB_USERNAME/DB_PASSWORD/DB_NAME 환경변수를 설정하세요.")

    # SQLAlchemy URL 객체를 사용하여 연결 정보 생성
    sa_url = URL.create(
            drivername="mysql+pymysql",
            username=user,
            password=pwd,
            host=host,
            port=int(port),
            database=db,
        )

    connect_args = {"connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "10"))}

    # Aiven 등 관리형 MySQL은 기본적으로 SSL 연결을 요구함
    # check_hostname을 False로 설정하여 SSL 암호화만 사용
    connect_args["ssl"] = {}

    engine = create_engine(
        sa_url,
        pool_pre_ping=True,  # 커넥션을 사용하기 전에 유효한지 확인
        pool_recycle=1800,   # 30분마다 커넥션 재활용
        pool_size=5,
        max_overflow=10,
        connect_args=connect_args,
    )
    return engine
