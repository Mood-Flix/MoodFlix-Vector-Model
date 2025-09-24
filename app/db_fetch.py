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
              COALESCE(TRIM(GROUP_CONCAT(DISTINCT k.name ORDER BY k.name SEPARATOR ' ')), '') AS keywords_text,
              COALESCE(TRIM(CONCAT_WS(' ',
                GROUP_CONCAT(r.content  ORDER BY r.created_at  SEPARATOR ' '),
                GROUP_CONCAT(tr.content ORDER BY tr.created_at SEPARATOR ' ')
              )), '') AS reviews_text
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
        conn.execute(text("SET SESSION group_concat_max_len = 1024*1024"))
        rows = conn.execute(sql2, {"limit": limit, "offset": offset}).mappings().all()

    items = []
    for r in rows:
        genres   = [g.strip() for g in (r["genre"] or "").split("|") if g and g.strip()]
        keywords = (r["keywords_text"] or "").split()
        reviews  = [r["reviews_text"]] if r["reviews_text"] else []
        items.append({
            "id": int(r["id"]),
            "title": r["title"],
            "overview": r["overview"] or "",
            "genres": genres,
            "keywords": keywords,
            "reviews": reviews
        })
    return items
