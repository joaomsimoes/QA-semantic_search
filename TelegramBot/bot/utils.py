import spacy
from coinmarketcapapi import CoinMarketCapAPI
from conn_db import *
import requests
import json

# Load the saved spacy model
nlp = spacy.load("./spacy-ner-model")

# Load the coin dictionary to match the names with the corresponding code
f = open("./coins.json")
coins = json.load(f)

# Keys
f = open("keys.json")
data = json.load(f)


def coin_ner(text):
    """Receives the message from the user and return the information
    about the coin"""
    doc = nlp(text)
    for ent in doc.ents:
        coin = ent.text

    # coinmarketcap-api
    cmc = CoinMarketCapAPI(data["CoinMarketCapAPI"])

    # The api expects the coin code, so it is needed to verify
    # what the user wrote
    for key, value in coins.items():
        if coin.lower() == value.lower():
            coin = value
            break
        elif coin.lower() == key.lower():
            coin = value
            break

    # Make the request and receive the answer
    r = cmc.cryptocurrency_info(symbol=coin)
    answer = repr(r.data[coin.upper()]['description'])
    answer = answer[1:-1]   # remove '' from beginning and end

    return answer


def semantic_api(query):
    result = query_cache(query)
    if result:
        return result[0]

    else:
        answer = requests.get('http://index-api:8000/', params={'query': str(query)}).json()
        try:
            if answer[0]:
                push_cache(query, answer[0], answer[1])
                return answer
        except:
            return []