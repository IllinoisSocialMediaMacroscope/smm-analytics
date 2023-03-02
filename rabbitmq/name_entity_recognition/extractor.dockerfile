FROM ubuntu:18.04

RUN mkdir -p /scripts
WORKDIR /scripts

# copy paste python scripts
COPY . ./

# install dependency libraries
RUN apt-get update
RUN apt-get -y install python3-pip wget unzip

# install dependency libraries and download required data
RUN pip3 install -r requirement.txt

# download glove data
RUN cd ./data && wget http://nlp.stanford.edu/data/glove.twitter.27B.zip && unzip glove.twitter.27B.zip

# Command to be run when container is run
# Can add heartbeat to change the refresh rate
CMD python3 SmmExtractor.py --heartbeat 40

ENV MAIN_SCRIPT="SmmExtractor.py"
