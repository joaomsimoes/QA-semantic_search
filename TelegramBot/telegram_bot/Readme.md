# Telegram Bot

One of the main problems from the transformers architectures is that it needs a lot of GPU power to be fast. Because of my free tier limit, I deployed the bot in a VM with CPU's only. To overcome the waiting time for a query, I decided to cache the answers. Also, every time anyone asks something new, it will cache it in a database.

## Dependencies
```
python-telegram-bot
sqlalchemy
pymysql
mysql-connector-python
requests
```

## Run locally
```
python main.py
```

## Build Docker container
```
docker build . -t <USER>/<REPO>:<TAG>
```