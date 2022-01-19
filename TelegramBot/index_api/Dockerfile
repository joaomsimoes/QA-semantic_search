FROM  nvidia/cuda:11.0-runtime-ubuntu20.04

RUN apt-get update && apt-get install -y \
    pip \
    python3.7

WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "index-api:app", "--host", "0.0.0.0", "--port", "8000"]