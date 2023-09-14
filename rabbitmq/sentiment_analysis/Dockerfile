FROM socialmediamacroscope/sentiment_analysis:base

RUN apt-get -qq -y update && apt-get -qq -y install cron

WORKDIR /scripts

COPY . ./

ENV RABBITMQ_HOST="rabbitmq"

# Install pyClowder and any other python dependencies
RUN pip install --no-cache-dir -r requirement.txt \
&& python3 -m nltk.downloader -d /usr/local/share/nltk_data stopwords wordnet punkt  \
    averaged_perceptron_tagger vader_lexicon sentiwordnet \
&& chmod u+x ./clear_cache.sh \
&& chmod 0644 ./clear_cache_cron \
&& crontab ./clear_cache_cron

# wordnet cannot unzip fix
RUN unzip /usr/local/share/nltk_data/corpora/wordnet.zip -d /usr/local/share/nltk_data/corpora
