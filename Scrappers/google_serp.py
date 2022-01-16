import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
import pandas as pd
import json
import os
import time


path = './serps/'


def db_connection():
    f = open("db.json")
    data = json.load(f)
    engine = create_engine(data['connection'])

    return engine


def insert_sql(keyword=None, title=None, text=None, link=None):
    engine = db_connection()
    with engine.connect() as conn:
        for t in text:
            insert = f"INSERT INTO serps (keyword, text, title, link)" \
                     "VALUES (%s, %s, %s, %s)"
            ts = time.time()
            value = (keyword, t, title, link)
            # try:
            conn.execute(insert, value)
            # except:
            #     print('sql-error')


def get_info(file=None):
    df = pd.read_csv(path+file)
    info = []
    try:
        for i, k in zip(df.URL.items(), df.Keyword.items()):
            info.append((i[1], k[1]))

    except:
        print('no link')

    return info


def get_text(link=None):
    hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    req = urllib.request.Request(link, headers=hdr)
    html = urlopen(req, timeout=5)
    bs = BeautifulSoup(html, 'html.parser')
    text = []
    title = bs.find('title')

    for t in bs.find_all("p"):
        t = t.get_text()
        if len(t) > 60:
            t = t.encode().decode('utf8', 'replace')
            text.append(t)

    return text, title.string


for file in os.listdir(path):
    if file.endswith(".csv"):
        info = get_info(file)
        print(file)

        for inf in info:
            try:
                text, title = get_text(inf[0])
                insert_sql(keyword=inf[1], text=text, title=title, link=inf[0])
                print("new text - ", inf[0])
            except:
                print('erro')
