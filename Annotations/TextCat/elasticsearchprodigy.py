from elasticsearch import Elasticsearch, helpers
from db.conn_db import query
import requests
import os

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
index = 'reddit-texcat'

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
        res = requests.post('http://localhost:9200/redditprodigy/_delete_by_query',
                        json={
                            'query': {
                                'match_all': {}
                            }
                        })
        os.remove('reddit.txt')

    except:
        pass

    reddit_text = query()

    full_text = []
    for text in reddit_text:
        for sentence in text.split("."):
            full_text.append(sentence)

    chunk_size = 500

    for start_idx in range(0, len(full_text), chunk_size):
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
def search(query=None):
    bm25 = es.search(index=index, query={"match": {"text": query}},
                     size=500)

    for hit in bm25['hits']['hits']:
        with open('reddit.txt', mode='a+', encoding='utf8') as f:
            f.write(hit['_source']['text'] + '\n')


search('sell')
