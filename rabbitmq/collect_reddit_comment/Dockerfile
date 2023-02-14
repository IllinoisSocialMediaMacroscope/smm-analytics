FROM ubuntu:18.04

RUN apt-get -qq -y update && apt-get -qq -y install cron

RUN mkdir -p /scripts
WORKDIR /scripts

# copy paste python scripts
COPY . ./

ENV RABBITMQ_HOST="rabbitmq"

# install dependency libraries
RUN apt-get update
RUN apt-get -y install python3-pip

# install dependency libraries and download required data
RUN pip3 install -r requirement.txt

# cron job clean tmp folder
RUN chmod u+x ./clear_cache.sh
RUN chmod 0644 ./clear_cache_cron
RUN crontab ./clear_cache_cron