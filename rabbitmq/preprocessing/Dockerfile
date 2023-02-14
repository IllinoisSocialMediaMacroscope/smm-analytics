FROM python:3.7

RUN apt-get -qq -y update && apt-get -qq -y install cron

RUN mkdir -p /scripts
WORKDIR /scripts

COPY . ./

ENV RABBITMQ_HOST="rabbitmq"

RUN pip install --no-cache-dir -r requirement.txt
RUN python3 -m nltk.downloader -d /usr/local/share/nltk_data punkt stopwords averaged_perceptron_tagger

# cron job clean tmp folder
RUN chmod u+x ./clear_cache.sh
RUN chmod 0644 ./clear_cache_cron
RUN crontab ./clear_cache_cron