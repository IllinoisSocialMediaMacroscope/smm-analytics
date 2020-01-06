#!/usr/bin/env bash
export DOCKERIZED=TRUE
export AWS_ACCESSKEY=***REMOVED***
export AWS_ACCESSKEYSECRET=***REMOVED***
export TWITTER_CONSUMER_KEY=***REMOVED***
export TWITTER_CONSUMER_SECRET=***REMOVED***
export REDDIT_CLIENT_ID=***REMOVED***
export REDDIT_CLIENT_SECRET=***REMOVED***
export FLICKR_CONSUMER_KEY=***REMOVED***
export FLICKR_CONSUMER_SECRET=***REMOVED***
export BOX_CLIENT_ID=***REMOVED***
export BOX_CLIENT_SECRET=***REMOVED***
export DROPBOX_CLIENT_ID=***REMOVED***
export DROPBOX_CLIENT_SECRET=***REMOVED***
export GOOGLE_CLIENT_ID=***REMOVED***
export GOOGLE_CLIENT_SECRET=***REMOVED***

# subtitute this to a folder that you want to mount on; must be absolute path
export LOCAL_MOUNT_PATH=/Users/cwang138/Documents/Macroscope/smile_mounted_data
export BUCKET_NAME=macroscope-smile

# create the local_mount_path folder and bucket
if [ -d ${LOCAL_MOUNT_PATH}/${BUCKET_NAME} ]
then
    echo "Directory exists. Continue..."
else
    echo "Error: Directory does not exists. Create one"
    mkdir ${LOCAL_MOUNT_PATH}/${BUCKET_NAME}
fi

docker-compose -f docker-compose-smile.yml up