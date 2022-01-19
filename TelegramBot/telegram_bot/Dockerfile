FROM python:3.8

COPY . /app
COPY requirements.txt /app/requirements.txt

WORKDIR /app

USER root

RUN pip install --upgrade pip
RUN pip install -U pip setuptools wheel
RUN pip install -U spacy
RUN pip install -r requirements.txt

CMD ["python", "main.py"]