# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
WORKDIR /tweet_processor
COPY . .
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "-m", "main"]