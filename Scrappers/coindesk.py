import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from lxml import etree
from datetime import datetime
import json


def insert_sql(text=None, link=None, time=None):
    f = open("db.json")
    data = json.load(f)
    engine = create_engine(data['connection'] + "coindesk")
    with engine.connect() as conn:
        for t in text:
            insert = f"INSERT INTO coindesk (text, time, link)" \
                     "VALUES (%s, %s, %s)"
            values = (t, time, link)
            conn.execute(insert, values)


def get_links(url=None):
    links = set()
    hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    req = urllib.request.Request(url, headers=hdr)
    html = urlopen(req, timeout=5)
    print(html.status)

    bs = BeautifulSoup(html, 'lxml')
    urls = bs.find_all('loc')
    for url in urls:
        html = urlopen(url.string)
        bs = BeautifulSoup(html, 'lxml')
        link = bs.find_all('loc')
        for l in link:
            if '2021' in l.string:
                links.add(l.string)
                print(l)

    return links


def get_text(url=None):
    text = []
    hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    req = urllib.request.Request(url, headers=hdr)
    html = urlopen(req, timeout=5)
    html_status = html.status

    try:
        bs = BeautifulSoup(html, 'html.parser')
        for t in bs.find_all("p"):
            t = t.get_text()
            if len(t) > 50:
                t = t.encode().decode('utf8', 'ignore')
                text.append(t)

    except:
        print(f"{html_status}")

    return text, html_status


def get_time(url=None):
    hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    req = urllib.request.Request(url, headers=hdr)
    html = urlopen(req, timeout=5)

    try:
        bs = BeautifulSoup(html, 'html.parser')
        dom = etree.HTML(str(bs))
        time = dom.xpath('//*[@id="fusion-app"]/div/div[2]/main/article/div/header/div[2]/div/div[4]/div[2]/div/span')[
            0].text
        time = time.replace(' at', '')
        date_time = datetime.strptime(time[:-9], '%b %d, %Y %H:%M')

    except:
        print("ERRO - get-time")

    return date_time


def text_file(blog_name=None, text=None):
    with open(blog_name + '.txt', mode='a+', encoding='utf8') as f:
        for t in text:
            t = t.replace('\n', '')
            f.write(t + '\n')


blogs = {'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/sitemap-index/?outputType=xml'
         }

for blog_name, blog_url in blogs.items():
    links = get_links(url=blog_url)
    for link in links:
        try:
            print(link)
            text, html_status = get_text(url=link)
            time = get_time(url=link)
            if html_status == 200:
                # insert_sql(text=text, link=link, time=time)
                text_file(blog_name, text)
            else:
                break
        except:
            print('erro ' + str(link))
