import json
from sqlalchemy import create_engine


def db_connection():
    f = open("db.json")
    data = json.load(f)
    engine = create_engine(data['connection'] + "scrapper")

    return engine


def db_query():
    engine = db_connection()
    with engine.connect() as cursor:
        result = cursor.execute("SELECT text FROM serps")
        results = result.fetchall()

        text = [i[0] for i in results]
        reddit_text = list(set(text))

        return reddit_text
