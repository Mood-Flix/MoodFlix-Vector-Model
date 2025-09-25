# app/db_fetch.py
from sqlalchemy import text
from sqlalchemy.engine import Engine

def fetch_movies_for_embedding(engine: Engine, offset: int, limit: int):
    sql = text("""
        SELECT
          m.id,
          ANY_VALUE(m.title)    AS title,
          ANY_VALUE(m.overview) AS overview,
          ANY_VALUE(m.genre)    AS genre,
          COALESCE(
            TRIM(GROUP_CONCAT(DISTINCT k.name ORDER BY k.name SEPARATOR ' ')),
            ''
          ) AS keywords_text,
          COALESCE(
            TRIM(CONCAT_WS(' ',
              GROUP_CONCAT(r.content  ORDER BY r.created_at  SEPARATOR ' '),
              GROUP_CONCAT(tr.content ORDER BY tr.created_at SEPARATOR ' ')
            )),
            ''
          ) AS reviews_text
        FROM movies m
        LEFT JOIN movie_keywords mk ON mk.movie_id = m.id
        LEFT JOIN keywords k        ON k.id = mk.keyword_id
        LEFT JOIN reviews r         ON r.movie_id = m.id
        LEFT JOIN tmdb_reviews tr   ON tr.movie_id = m.id
        WHERE m.adult = b'0'
        GROUP BY m.id
        ORDER BY m.id
        LIMIT :limit OFFSET :offset
    """)

    with engine.begin() as conn:
        # 긴 리뷰/키워드 합치기 위해 group_concat 길이 확장
        conn.execute(text("SET SESSION group_concat_max_len = 1024*1024"))
        rows = conn.execute(sql, {"limit": limit, "offset": offset}).mappings().all()

    # 반환 형식: id, title, overview, genres(list), keywords(list), reviews(list)
    out = []
    for r in rows:
        genres = [g.strip() for g in (r["genre"] or "").split("|") if g.strip()]
        keywords = [k for k in (r["keywords_text"] or "").split(" ") if k]
        reviews  = [rv for rv in (r["reviews_text"]  or "").split(" ") if rv]
        out.append({
            "id": r["id"],
            "title": r["title"],
            "overview": r["overview"],
            "genres": genres,
            "keywords": keywords,
            "reviews": reviews,
        })
    return out