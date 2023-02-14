FROM python:3.7

RUN mkdir -p /scripts
WORKDIR /scripts

COPY . ./

ENV RABBITMQ_HOST="rabbitmq"

RUN pip install --no-cache-dir -r requirement.txt