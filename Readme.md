# Semantic Search - Cryptobot

Cryptocurrency has been an emerging technology that raises lots of questions. But unfortunately, it isn't easy to understand all the terms, how it works and terminology.

I started to be more interested in NLP for some months now. I was looking forward to building a new project using the transformers library. I found interesting the idea of using semantic to find your answers.

## The timeline

1. Scrape the data
2. Build a semantic search engine
3. Deploy it with a telegram bot


### Scrape the data

To scrape all necessary data, I used a trial account from Ahrefs to access the most common queries and its top 10 websites ranked by google.

Easy peasy!

### Build a semantic search engine

This was the most challenging aspect. I needed to understand the transformer architecture, how sentences transformers work and how to index vectors to use them with the telegram bot.

For the transformers, I used the huggingface and sentence-transformers libraries. This was fun and good to learn. I used [Mastering Transformers](https://www.packtpub.com/product/mastering-transformers/9781801077651) and [Getting Started with Google BERT](https://www.packtpub.com/product/getting-started-with-google-bert/9781838821593) to learn all I could. The documentations from both libraries are also excellent.

Indexing the data was the challenging aspect. First, I tried Haystack, but it was bugging a lot and limiting
to do what I wanted. Next, I tried Faiss and Pinecone, which are good libraries (Pinecone has a good filter system), but I used HNSW at the end. I understood that the most crucial element is vectorising your data with the transformers. Indexing your data is just a question of how fast you can query it. 


### Telegram Bot

I didn't want to focus too much on the Bot for this project. In my opinion, it was just a fun way to share my project.

I started to build it with Rasa. It was easy and fast. But I could not deploy it.

For that reason, I used telegram-python-bot to build my chatbot.  