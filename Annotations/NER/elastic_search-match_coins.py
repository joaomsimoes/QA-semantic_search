from elasticsearch import Elasticsearch, helpers
from db.conn_db import query
import requests
import os

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Index data, if the index does not exists
if not es.indices.exists(index="redditprodigy"):

    es_index = {
        "mappings": {
            "properties": {
                "text": {
                    "type": "text"
                },
            }
        }
    }

    es.indices.create(index='redditprodigy', body=es_index)


if es.indices.exists(index="redditprodigy"):

    try:
        os.remove('coin_reddit.txt')

        res = requests.post('http://localhost:9200/redditprodigy/_delete_by_query',
                        json={
                            'query': {
                                'match_all': {}
                            }
                        })
    except:
        pass

    reddit_text = query()

    chunk_size = 500

    for start_idx in range(0, len(reddit_text), chunk_size):
        end_idx = start_idx+chunk_size

        bulk_data = []
        for id, text in enumerate(reddit_text):
            bulk_data.append({
                "_index": 'redditprodigy',
                "_id": id,
                "_source": {
                    "text": text,
                }
            })

        helpers.bulk(es, bulk_data)


# Search query
def search(query=None):
    bm25 = es.search(index="redditprodigy", query={"match": {"text": query}},
                     size=500)

    for hit in bm25['hits']['hits']:
        with open('coin_reddit.txt', mode='a+', encoding='utf8') as f:
            f.write(hit['_source']['text'] + '\n')
