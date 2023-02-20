FROM python:3.8.5

RUN mkdir -p /scripts
WORKDIR /scripts

COPY . ./

RUN pip install --no-cache-dir -r requirement.txt


# Command to be run when container is run
# Can add heartbeat to change the refresh rate
CMD python3 SmmExtractor.py --heartbeat 40

ENV MAIN_SCRIPT="SmmExtractor.py"
