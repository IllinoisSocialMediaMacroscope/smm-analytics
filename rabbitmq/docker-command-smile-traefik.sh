# system setting
export DOCKERIZED=true

# if use AWS algorithm, then you must use a static IP address
export LOCAL_ALGORITHM=true

# single user version vs multiple users
export SINGLE_USER=false

#set up home directory
export HOME=/your/home/directory

#set server info
export SERVER=smm.server.com

# settings for CILOGON
export CILOGON_CLIENT_ID=<<cilogon id>>
export CILOGON_CLIENT_SECRET=<<cilogon client secret>>
export CILOGON_CALLBACK_URL=<<ci logon callback url>>

# if the minio-api.server doesn't work, it should ip address and port
# export MINIO_URL=http://xxx.xxx.xxx.xxx:9000
# export MINIO_PUBLIC_ACCESS_URL=http://xxx.xxx.xxx.xxx:9000
export MINIO_URL=https://minio-api.${SERVER}
export MINIO_PUBLIC_ACCESS_URL=https://minio-api.${SERVER}
export BUCKET_NAME=macroscope-smile
# if the graphql.server doesn't work, it should use ip address and port
#export SMILE_GRAPHQL_URL=http://xxx.xxx.xxx.xxx:5050/graphql
export SMILE_GRAPHQL_URL=https://graphql.${SERVER}/graphql

# create mounted volumes on host machine
mkdir -p ${HOME}/smile_data/${BUCKET_NAME}
mkdir -p ${HOME}/smile_user
mkdir -p ${HOME}/smile

export RABBITMQ_HOST=${SERVER}
export RABBITMQ_URL=amqp://${SERVER}
export REDIS_URL=redis://redis

# email notification
#export EMAIL_HOST=<<email host>>
#export EMAIL_PORT=465
#export EMAIL_FROM_ADDRESS=<<email from address>>
#export EMAIL_PASSWORD=<<email password>>

# align with AWS
export AWS_ACCESSKEY=<<aws_accesskey>>
export AWS_ACCESSKEYSECRET=<<aws_accesskeysecret>>

# social media platforms
export REDDIT_CLIENT_ID=<<reddit client id>>
export REDDIT_CLIENT_SECRET=<<reddit client secret>>
export REDDIT_CALLBACK_URL=<<reddit callback url>>
#export TWITTER_CONSUMER_KEY=<<twitter consumer key>>
#export TWITTER_CONSUMER_SECRET=<<twitter consumer secret>>
export TWITTER_V2_CLIENT_ID=<<twitter v2 client id>>
export TWITTER_V2_CLIENT_SECRET=<<twitter v2 client secret>>
export TWITTER_V2_CALLBACK_URL=<<twitter v2 callback url>>

# export
export BOX_CLIENT_ID=<box client id>
export BOX_CLIENT_SECRET=<<box client secret>>
export DROPBOX_CLIENT_ID=<<dropbox client id>>
export DROPBOX_CLIENT_SECRET=<<dropbox client secret>>
export GOOGLE_CLIENT_ID=<<google client id>>
export GOOGLE_CLIENT_SECRET=<<google client secret>>

export CLOWDER_BASE_URL=https://clowder.server.com/
export CLOWDER_GLOBAL_KEY=<<clowder global key>>
export CLOWDER_ON=false

# start
docker-compose -f docker-compose-smile-traefik.yml -d up

# stop
# docker-compose -f docker-compose-smile.yml down -v

# update latest image from docker hub
# docker-compose -f docker-compose-smile.yml pull
