import re
import html
import time
import requests
import random
from sqlalchemy import create_engine
from datetime import datetime
import json


def clean(text):
    # convert html escapes like &amp; to characters.
    text = html.unescape(text)
    # tags like <tab>
    text = re.sub(r'<[^<>]*>', ' ', text)
    # markdown URLs like [Some text](https://....)
    text = re.sub(r'\[([^\[\]]*)\]\([^\(\)]*\)', r'\1', text)
    # text or code in brackets like [0]
    text = re.sub(r'\[[^\[\]]*\]', ' ', text)
    # standalone sequences of specials, matches &# but not #cool
    text = re.sub(r'(?:^|\s)[&#<>{}\[\]+|\\:-]{1,}(?:\s|$)', ' ', text)
    # standalone sequences of hyphens like --- or ==
    text = re.sub(r'(?:^|\s)[\-=\+]{2,}(?:\s|$)', ' ', text)
    # sequences of white spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def reddit_connect():
    f = open("reddit.json")
    data = json.load(f)
    client_id = data["client_id"]
    secret = data["secret"]
    auth = requests.auth.HTTPBasicAuth(client_id, secret)
    data = {'grant_type': 'password',
            'username': data["data"]["username"],
            'password': data["data"]["password"]}
    headers = {'User-Agent': 'Crypto/0.0.1'}
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)
    token = res.json()['access_token']
    headers['Authorization'] = f'bearer {token}'

    return headers


def init_db_connection():
    f = open("db.json")
    data = json.load(f)
    engine = create_engine(data['connection'] + "scrapper")

    return engine


def last_name_id(subreddit=None, db=None):
    with db.connect() as conn:
        query = f"SELECT name FROM reddit WHERE name <> 'Null' and subreddit = '{subreddit}' " \
                f"ORDER BY id DESC LIMIT 1"
        result = conn.execute(query)
        last_name = result.fetchone()

        last_name = last_name.name if last_name != None else None

    return last_name


def reddit_request(subreddit=None, heads=None, db=None):
    api = 'https://oauth.reddit.com'

    #get last name from the table
    last_name = last_name_id(subreddit=subreddit, db=db)

    #if the table is empty, start to scrape from the first post
    if last_name != None:
        while True:
            last_name = last_name_id(subreddit=subreddit, db=db)
            res = requests.get(f'{api}/r/{subreddit}/new', headers=heads, params={'limit': 100, 'after': last_name})
            if res.json()['data']['dist'] == 0:
                break
            else:
                print(subreddit, ' - new post')
                post_to_db(res, subreddit)
                get_comments(res, subreddit, heads=heads)
                time.sleep(3)
    else:
        res_post = requests.get(f'{api}/r/{subreddit}/new', headers=heads, params={'limit': 100})
        time.sleep(2)
        print(res_post)
        try:
            post_to_db(res_post, subreddit)
            get_comments(res_post, subreddit, heads=heads)
            reddit_request(subreddit, heads, db)
        except:
            print("2 broke")


def post_to_db(res=None, subreddit=None):
    for post in res.json()['data']['children']:
        name = post['data']['name'],
        created_utc = datetime.fromtimestamp(post['data']['created_utc']),
        rsubreddit = post['data']['subreddit'],
        title = post['data']['title'],
        selftext = post['data']['selftext'],
        upvote_ratio = post['data']['upvote_ratio'],
        score = post['data']['score']

        text = clean(selftext[0])

        with db.connect() as conn:
            insert = f"INSERT INTO reddit (name, subreddit, title, selftext, upvote_ratio, score, created_utc)" \
                     "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            value = (name[0], rsubreddit[0], title[0], text, upvote_ratio[0], score, created_utc[0])
            conn.execute(insert, value)


def get_comments(res_post=None, subreddit=None, heads=None):
    api = 'https://oauth.reddit.com'
    for page in res_post.json()['data']['children']:
        id = page['data']['id']
        res_com = requests.get(f'{api}/r/{subreddit}/comments/{id}/', headers=heads, params={'limit': 100})
        time.sleep(2)
        print(subreddit, " - ", res_com)

        try:
            for comment in res_com.json()[1]['data']['children']:
                id = 'Null',
                created_utc = datetime.fromtimestamp(comment['data']['created_utc']),
                rsubreddit = comment['data']['subreddit'],
                title = 'Null',
                selftext = comment['data']['body'],
                upvote_ratio = 'Null'
                score = comment['data']['score']

                text = clean(selftext[0])

                if text != '[removed]' or text != '[deleted]':
                    with db.connect() as conn:
                        insert = f"INSERT INTO reddit (name, subreddit, title, selftext," \
                                 f" upvote_ratio, score, created_utc)" \
                                 "VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        value = (id[0], rsubreddit[0], title[0], text, upvote_ratio[0], score, created_utc[0])
                        conn.execute(insert, value)

            print(subreddit, ' - comments going')
        except:
            print(subreddit, " comments with problem")


db = init_db_connection()

subreddits = ['bitcoinbegginers',
              'bitcoincash', 'bitcoinca', 'bitcoin', 'dogecoin', 'cardano', 'crypto_general',
              'vechain', 'litecoinmarkets', 'coinbase', 'cryptotechnology', 'bitcoinmining',
              'bitcoinmarkets', 'bytecoin', 'ethtrader', 'cryptocurrency', 'cryptomoonshots']

for i in subreddits:
    print(i)
    heads = reddit_connect()
    reddit_request(subreddit=i, heads=heads, db=db)