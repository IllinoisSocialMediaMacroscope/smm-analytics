FROM ubuntu:18.04

# git clone autophrase algorithm
RUN apt-get update
RUN apt-get -y install git && apt-get -y install cron
RUN cd / && git clone https://github.com/IllinoisSocialMediaMacroscope/SMILE-AutoPhrase.git AutoPhrase

# overwrite
WORKDIR /AutoPhrase
COPY . ./

ENV RABBITMQ_HOST="rabbitmq"

# install dependency libraries
RUN apt-get -y install g++
RUN apt-get -y install openjdk-8-jdk
RUN apt-get -y install curl
RUN apt-get -y install python3-pip
RUN pip3 install -r requirement.txt

# switch work directory to be AutoPhrase
RUN /bin/bash -c "source compile.sh"

# cron job clean tmp folder
RUN chmod u+x ./clear_cache.sh
RUN chmod 0644 ./clear_cache_cron
RUN crontab ./clear_cache_cron
