#!/usr/bin/env bash

EXPORT AWS_ACCESSKEY=${YOUR AWS ACCESSKEY}
EXPORT AWS_ACCESSKEYSECRET=${YOUR AWS ACESSKEYSECRET}
...

# for minIO
docker run -p 9000:9000 -e "MINIO_ACCESS_KEY=" -e "MINIO_SECRET_KEY=" minio/minio server /data

docker-compose up