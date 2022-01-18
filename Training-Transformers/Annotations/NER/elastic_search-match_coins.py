from elasticsearch import Elasticsearch, helpers
from db.conn_db import query
import requests
import json
import os
from tqdm import tqdm

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
index = 'coin-ner'

# Index data, if the index does not exists
if not es.indices.exists(index=index):

    es_index = {
        "mappings": {
            "properties": {
                "text": {
                    "type": "text"
                },
            }
        }
    }

    es.indices.create(index=index, body=es_index)


if es.indices.exists(index=index):

    try:
        os.remove('coin_reddit.txt')

        res = requests.post(f'http://localhost:9200/{index}/_delete_by_query',
                        json={
                            'query': {
                                'match_all': {}
                            }
                        })
    except:
        pass

    reddit_text = query()

    full_text = set()
    for text in reddit_text:
        for sentence in text.split("."):
            if len(sentence) > 20:
                full_text.add(sentence)

    chunk_size = 500

    for start_idx in tqdm(range(0, len(full_text), chunk_size)):
        end_idx = start_idx+chunk_size

        bulk_data = []
        for id, text in enumerate(full_text):
            bulk_data.append({
                "_index": index,
                "_id": id,
                "_source": {
                    "text": text,
                }
            })

        helpers.bulk(es, bulk_data)


# Search query
def search(coin):
    bm25 = es.search(index=index, query={"match": {"text": coin}},
                     size=20)

    for hit in bm25['hits']['hits']:
        with open('coin_reddit.txt', mode='a+', encoding='utf8') as f:
            f.write(hit['_source']['text'] + '\n')


if __name__ == '__main__':
    f = open("coins.json")
    coins = json.load(f)

    for key, value in tqdm(coins.items()):
        search(key)
        search(value)
