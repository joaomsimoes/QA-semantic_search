# Telegram bot. The CryptoBot!

Finally, joining all the pieces.

I divided it into the Telegram bot and the Index API service. The bot is hosted in a GCP VM with docker-compose.

## 1. Telegram
I used the telegram-python-bot to build the bot. I didn't lose too much time with this library. My goal was to have something working as an MVP.
## 2. Index API
All the work from the semantic search came here. So I decided to separate it from the telegram bot to run in a different container.


## Run
```
sudo docker-compose up -d
```