# Index-API

The API receives a get request, processes the query, and returns an answer. <br>
<br>The model will find the best 50 passages corresponding to the query. Then re-rank the top 15 passages with a  Cross-encoder model (this will give better accuracy). From this last list, get the most frequent webpage. Query all the text from that webpage. Re-rank the top 5 passages and finally summarize them with transformers.
<br>I tried to take fewer steps initially, but the quality was not so good. For example, it overlapped some passages and sometimes had different meanings.
<br>**I was looking for quality, not for speed**<br>
Another option that I tried was to get the most frequent link from the first 50 passages. Then, query all the text from that link and summarize it. But again, re-rank makes all the magic.<br>
<br>I hosted locally the corpus_sentences and the hnsw index file, created with the notebook. The transformer models are also stored locally.
## Dependencies
```
transformers
sentence-transformers
hnswlib
sqlalchemy
pymysql
mysql-connector-python
fastapi
uvicorn
gunicorn
```

## Run locally
```
uvicorn index-api:app
```

## Build Docker container
```
docker build . -t <USER>/<REPO>:<TAG>
```