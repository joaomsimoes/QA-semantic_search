import json
from sqlalchemy import create_engine
import mysql.connector
import hashlib
import re


def db_connection(database=None):
    f = open("db.json")
    data = json.load(f)
    engine = create_engine(data['connection'] + database)

    return engine


def query_meme():
    engine = db_connection('scrapper')
    with engine.connect() as cursor:
        result = cursor.execute("SELECT link FROM memes ORDER BY RAND() LIMIT 1")
        results = result.fetchall()

        return results[0][0]


#####################

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


###################


def clean_text(text):
    mapping = {'?': '', ' ': '', '!': ''}
    text = text.lower()
    for key, value in mapping.items():
        text.replace(key, value)

    return text


def query_cache(query):
    query = re.sub(r"[^a-zA-Z0-9]", "", query).lower()
    hash_query = hashlib.md5(query.encode()).hexdigest()
    engine = db_connection("hnsw")
    with engine.connect() as cursor:
        results = cursor.execute(
            f"SELECT answer, link FROM hnsw.cache WHERE hash = '{hash_query}';"
        )
        result = results.fetchall()

        return result


def push_cache(query, answer, link):
    text = re.sub(r"[^a-zA-Z0-9]", "", query).lower()
    hash_query = hashlib.md5(text.encode()).hexdigest()
    engine = db_connection("hnsw")
    with engine.connect() as cursor:
        insert = f"INSERT INTO hnsw.cache (hash, query, answer, link)" \
                 f"VALUES(%s, %s, %s, %s)"
        values = (hash_query, query, answer, link)
        cursor.execute(insert, values)

