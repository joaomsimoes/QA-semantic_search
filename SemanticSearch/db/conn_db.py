import json
from sqlalchemy import create_engine
import mysql.connector


def db_connection(database=None):
    f = open("db.json")
    data = json.load(f)
    engine = create_engine(data['connection'] + database)

    return engine


def query_scrapper():
    engine = db_connection("hnsw")
    with engine.connect() as cursor:
        result = cursor.execute(f"SELECT text, link FROM hnsw.index")
        results = result.fetchall()

        return results


def query_hnsw(ids):
    engine = db_connection("hnsw")
    with engine.connect() as cursor:
        results = cursor.execute(
            f"SELECT text, link FROM hnsw.hnsw_index WHERE id IN {ids};"
        )
        result = results.fetchall()

        return result

def query_context(link):
    engine = db_connection("hnsw")
    with engine.connect() as cursor:
        results = cursor.execute(
            f"SELECT text FROM hnsw.hnsw_index WHERE link = '{link}';"
        )
        result = results.fetchall()

        return result

