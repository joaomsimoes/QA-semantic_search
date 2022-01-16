FROM python:3.7-slim

COPY . /app
COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]