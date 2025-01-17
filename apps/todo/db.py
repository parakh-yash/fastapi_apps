import psycopg
from psycopg.rows import class_row
import os 

def execute_query(query: str, cls, params = None):
    db_config = {
        "host": os.environ.get("HOST"),
        "port": os.environ.get("PORT"),
        "dbname": os.environ.get("DBNAME"),
        "user": os.environ.get("USER"),
        "password": os.environ.get("PASSWORD")
    }
    with psycopg.connect(**db_config) as conn:
        with conn.cursor(row_factory=class_row(cls)) as cur:
            cur.execute(query, params)
            result = cur.fetchall()
            conn.commit()
            return result
