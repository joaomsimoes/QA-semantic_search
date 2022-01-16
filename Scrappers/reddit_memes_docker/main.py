import requests
import json
import shutil
from sqlalchemy import create_engine


def init_db_connection():
    f = open("db.json")
    data = json.load(f)
    engine = create_engine(data['connection'])

    return engine


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


def get_memes():
    db = init_db_connection()

    subreddit = 'cryptocurrencymemes'
    api = 'https://oauth.reddit.com'
    headers = reddit_connect()
    res = requests.get(f'{api}/r/{subreddit}/new', headers=headers, params={'limit': 100})

    for post in res.json()['data']['children']:
        image = post['data']['url']

        file_type = ['.jpeg', '.jpg', '.png', '.gif']

        for type in file_type:
            if type in image:
                with db.connect() as conn:
                    insert = f"INSERT INTO memes (link)" \
                             "VALUES (%s)"
                    value = (image)
                    conn.execute(insert, value)


if __name__ == '__main__':
    get_memes()
