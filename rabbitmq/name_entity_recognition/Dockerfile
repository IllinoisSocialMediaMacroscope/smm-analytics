FROM socialmediamacroscope/name_entity_recognition:base

WORKDIR /scripts

# copy paste python scripts
COPY . ./

ENV RABBITMQ_HOST="rabbitmq"

# install dependency libraries
RUN apt-get update \
&& apt-get -y install python3-pip wget unzip cron \
# install dependency libraries and download required data
&& pip3 install -r requirement.txt \
# download glove data
&& cd ./data && wget http://nlp.stanford.edu/data/glove.twitter.27B.zip && unzip glove.twitter.27B.zip \
# cron job clean tmp folder \
&& cd ../ \
&& chmod u+x ./clear_cache.sh \
&& chmod 0644 ./clear_cache_cron \
&& crontab ./clear_cache_cron