FROM ubuntu:18.04

RUN mkdir -p /scripts
WORKDIR /scripts

# copy paste python scripts
COPY . ./

ENV RABBITMQ_HOST="rabbitmq"

# install dependency libraries
RUN apt-get update
RUN apt-get -y install python3-pip wget unzip cron

# install dependency libraries and download required data
RUN pip3 install -r requirement.txt

# download glove data
RUN cd ./data && wget http://nlp.stanford.edu/data/glove.twitter.27B.zip && unzip glove.twitter.27B.zip

# cron job clean tmp folder
RUN chmod u+x ./clear_cache.sh
RUN chmod 0644 ./clear_cache_cron
RUN crontab ./clear_cache_cron