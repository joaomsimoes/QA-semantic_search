FROM python:3.7-slim-buster

COPY requirements.txt /app/

WORKDIR /app
COPY . /app

RUN apt-get update
RUN pip install -r requirements.txt
RUN pip install prodigy -f prodigy-wheel/

ENV PRODIGY_HOME=/app
ENV PRODIGY_HOST=0.0.0.0
ENV PRODIGY_PORT=80

CMD ["python", "-m", "prodigy", "semanticsearch", "semanticsearch", "-F", "prodigy_semanticsearch.py"]
