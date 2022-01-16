import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
import json


def init_db_connection():
    f = open("db.json")
    data = json.load(f)
    engine = create_engine(data['connection'])

    return engine


def insert_sql(text=None, link=None, db=None):
    with db.connect() as conn:
        for t in text:
            insert = f"INSERT INTO wikibit (text, link)" \
                     "VALUES (%s, %s)"
            value = (t, link)
            conn.execute(insert, value)


def get_links(url='https://en.bitcoinwiki.org/index.php?title=Special:AllPages&from=.bit'):
    links = set()

    hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    req = urllib.request.Request(url, headers=hdr)
    html = urlopen(req, timeout=5)
    bs = BeautifulSoup(html, 'html.parser')
    for url in bs.find_all('a'):
        if 'href' in url.attrs:
            new_page = url.attrs['href']
            links.add(new_page)

    next_page = '/index.php?title=Special:AllPages&amp;from=Arcona'
    while True:
        if next_page == '/index.php?title=Special:AllPages&from=Zeusshield':
            break
        html = urlopen('https://en.bitcoinwiki.org'+str(next_page), timeout=5)
        bs = BeautifulSoup(html, 'html.parser')
        find_next_page = bs.find_all(title='Special:AllPages')[1]
        next_page = find_next_page.attrs['href']
        for url in bs.find_all('a'):
            if 'href' in url.attrs:
                new_page = url.attrs['href']
                links.add(new_page)
                print(new_page)

    return links


def get_text(url=None):
    text = []
    hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    req = urllib.request.Request('https://en.bitcoinwiki.org'+str(url), headers=hdr)
    html = urlopen(req, timeout=5)

    bs = BeautifulSoup(html, 'html.parser')
    for t in bs.find_all("p"):
        t = t.get_text()
        if len(t) > 60:
            t = t.encode().decode('utf8', 'ignore')
            text.append(t)
    return text


blogs = {'bitcoinwiki': 'https://en.bitcoinwiki.org/wiki/Special:WhatLinksHere/Main_Page'}

db = init_db_connection()

for blog_name, blog_url in blogs.items():
    print("\n\n+++++++" + blog_name + "+++++++\n\n")
    links = get_links()
    for link in links:
        try:
            print(link)
            text = get_text(url=link)
            insert_sql(text=text, link=link, db=db)
        except:
            print('erro')


# with db.connect() as conn:
#     insert = f"CREATE TABLE {k} (" \
#              f"id INT NOT NULL AUTO_INCREMENT, " \
#              f"text TEXT NOT NULL, " \
#              f"blog_name TEXT NOT NULL, " \
#              f"link TEXT NOT NULL, " \
#              f"PRIMARY KEY (id))"
#     conn.execute(insert)

