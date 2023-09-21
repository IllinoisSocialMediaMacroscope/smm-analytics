FROM ubuntu:20.04

# git clone autophrase algorithm
RUN apt-get update \
&& apt-get -y install git && apt-get -y install cron \
&& cd / && git clone https://github.com/IllinoisSocialMediaMacroscope/SMILE-AutoPhrase.git AutoPhrase

# overwrite
WORKDIR /AutoPhrase
COPY . ./

ENV RABBITMQ_HOST="rabbitmq"

# install dependency libraries
RUN apt-get -y update \
&& apt-get -y install g++ openjdk-8-jdk curl python3-pip \
&& pip3 install -r requirement.txt \
# switch work directory to be AutoPhrase
&& /bin/bash -c "source compile.sh" \
# cron job clean tmp folder
&& chmod u+x ./clear_cache.sh \
&& chmod 0644 ./clear_cache_cron \
&& crontab ./clear_cache_cron
