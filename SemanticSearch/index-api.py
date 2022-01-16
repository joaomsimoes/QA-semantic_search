import hnswlib
from sentence_transformers import SentenceTransformer, CrossEncoder
from transformers import pipeline
from fastapi import FastAPI
from db.conn_db import query_hnsw
from numpy import median
from collections import Counter
import pickle
import torch

print(torch.cuda.is_available())

app = FastAPI(title="SemanticSearch-API", debug=True, version="0.1")

print("loading corpus")
with open('./embeddings/embeddings.pkl', "rb") as fIn:
    cache_data = pickle.load(fIn)
    corpus_sentences = cache_data['sentences']

print("loading index")
embedding_size = 768
top_k_hits = 30
len_corpus = 104120

index = hnswlib.Index(space='cosine', dim=embedding_size)
index.load_index("hnswlib.bin", max_elements=len_corpus)

print("loading models")
model_embedder = SentenceTransformer('./models/msmarco-distilbert-dot-v5', device='cuda')
model_cross = CrossEncoder('models/ms-marco-MiniLM-L-12-v2', device='cuda')
model_sum = './models/t5-base'
sum_pipe = pipeline('summarization', model=model_sum, tokenizer=model_sum,
                    framework='pt', device=0)


@app.get('/')
async def semanticsearch(query):
    # Embed the query into vector space
    question_embedding = model_embedder.encode([query]).tolist()

    # Search with HNSW for the best passsage
    corpus_ids, distances = index.knn_query(question_embedding, k=top_k_hits)
    hits = [{'corpus_id': id, 'score': 1-score} for id, score in zip(corpus_ids[0], distances[0])]

    # Append the passages
    passages_id = []
    score_total = []
    for hit in hits[0:top_k_hits]:
        passages_id.append(hit['corpus_id'])
        score_total.append(hit['score'])

    mean_score = median(score_total)

    if mean_score > 0.81:

        # Get the links from the passages
        db_results = query_hnsw(tuple(passages_id))
        passages = [i[0] for i in db_results]

        # Use cross encoder to rank the best passages
        model_inputs = [[query, passage] for passage in passages]
        scores = model_cross.predict(model_inputs)

        results = [{'input': inp, 'score': score} for inp, score in zip(model_inputs, scores)]
        results = sorted(results, key=lambda x: x['score'], reverse=True)

        # Append the pages links
        pages = []
        for hit in results[0:10]:
            for i in db_results:
                if i[0] == hit['input'][1]:
                    pages.append(i[1])

        # Get the most frequent page
        most_frequent = Counter(pages).most_common(1)[0][0]

        # Get all the text from that page
        page_context_results = query_context(most_frequent)
        page_context = [i[0] for i in page_context_results]

        # Rerank the best text according our query
        model_inputs = [[query, context] for context in page_context]
        scores = model_cross.predict(model_inputs)

        results = [{'input': inp, 'score': score} for inp, score in zip(model_inputs, scores)]
        results = sorted(results, key=lambda x: x['score'], reverse=True)

        context = []
        for hit in results[0:7]:
            context.append(hit['input'][1].capitalize())

        # Summarize the context
        answer = sum_pipe(
            f"question: {query} context: {context}",
            num_beams=4,
            do_sample=True,
            temperature=1.4,
            min_length=60,
            max_length=300
        )

        # Text formating
        answer = answer[0]['summary_text'].replace(' . ', '.')
        answer = answer.split('.')
        answer = [text.capitalize() for text in answer]
        answer = '. '.join(answer)

        print(query, answer, most_frequent, mean_score)

        return answer, most_frequent, mean_score

    else:
        return mean_score