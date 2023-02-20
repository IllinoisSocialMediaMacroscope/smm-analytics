FROM python:3.8.5

RUN mkdir -p /scripts
WORKDIR /scripts

COPY . ./

# Install pyClowder and any other python dependencies
RUN pip install --no-cache-dir -r requirement.txt
RUN python3 -m nltk.downloader -d /usr/local/share/nltk_data stopwords wordnet punkt averaged_perceptron_tagger \
vader_lexicon sentiwordnet

# wordnet cannot unzip fix
RUN unzip /usr/local/share/nltk_data/corpora/wordnet.zip -d /usr/local/share/nltk_data/corpora

# Command to be run when container is run
# Can add heartbeat to change the refresh rate
CMD python3 SmmExtractor.py --heartbeat 40

ENV MAIN_SCRIPT="SmmExtractor.py"
