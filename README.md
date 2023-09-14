[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# Social Media Macroscope Analytics
Welcome to the Social Media Macroscope Analytics repository! 
Here, you'll find the essential analytics components that power various projects within the Social Media Macroscope 
ecosystem, such as the SMILE tool, BAE tool, and more. Our analytics suite is designed to provide powerful insights 
and data-driven solutions for social media research and beyond.

## Get Started
### Deploying SMILE
SMILE can be deployed using docker-compose. 
In this repository, there are two ways of deploying it, 
one is using traefik, and the other is a conventional way using nginx.
[Traefik](https://traefik.io/traefik/) is s a modern reverse proxy and 
load balancer that makes deploying microservices easy, and is designed to be 
as simple as possible to operate. 
It integrates with infrastructure components and configures itself automatically and dynamically.

### Using Docker Compose with Nginx (Deprecating soon)
#### Set up environment variables
- Use the script [docker-compose-smile.sh](./rabbitmq/docker-command-smile.sh)
- Alternatively, manually set following environment variables that start docker-compose with `docker-compose-smile.yml`
  - environment variable information is in the script
- Following code block includes the setups for the local directory and this can be modified based on the convenience
- Note that some of the configuration variables are optional

### Using Docker Compose with traefik (Recommended)
- Use the script [docker-compose-smile-traefik.sh](./rabbitmq/docker-command-smile-traefik.sh) 
- Alternatively, manually set the following environment variables then run docker-compose using the 
  `docker-compose-smile-traefik.yml`
- Note that some of the configuration variables are optional

#### Optional environment variables
- System setting. Set to true to use standalone containerized SMILE.
  - DOCKERIZED=true 
- If using algorithm deployed on AWS, then you must use a static IP address.
  - LOCAL_ALGORITHM=true
- Single user mode vs multiple users mode.
  - SINGLE_USER=false 
- Settings for CILOGON (this section is not required if running in single user mode)
  - CILOGON_CLIENT_ID={{cilogon id}}
  - CILOGON_CLIENT_SECRET={{cilogon client secret}}
  - CILOGON_CALLBACK_URL={{ci logon callback url}}
- Configure email server to enable capability of sending email notifications for long running jobs.
  - EMAIL_HOST={{email host}}
  - EMAIL_PORT=465 
  - EMAIL_FROM_ADDRESS={{email from address}}
  - EMAIL_PASSWORD={{email password}}
- MINIO access keys and secret. Can be set to align with AWS S3 access keys and secret.
  - AWS_ACCESSKEY={{aws_accesskey}}
  - AWS_ACCESSKEYSECRET={{aws_accesskeysecret}}
- Social media platforms configurations.
  - REDDIT_CLIENT_ID={{reddit client id}}
  - REDDIT_CLIENT_SECRET={{reddit client secret}}
  - REDDIT_CALLBACK_URL={{reddit callback url}}
  - TWITTER_CONSUMER_KEY={{twitter consumer key}}
  - TWITTER_CONSUMER_SECRET={{twitter consumer secret}}
  - TWITTER_V2_CLIENT_ID={{twitter v2 client id}}
  - TWITTER_V2_CLIENT_SECRET={{twitter v2 client secret}}
  - TWITTER_V2_CALLBACK_URL={{twitter v2 callback url}}
- Cloud storage platforms configurations (Optional)
  - BOX_CLIENT_ID=<box client id>
  - BOX_CLIENT_SECRET={{box client secret}}
  - DROPBOX_CLIENT_ID={{dropbox client id}}
  - DROPBOX_CLIENT_SECRET={{dropbox client secret}}
  - GOOGLE_CLIENT_ID={{google client id}}
  - GOOGLE_CLIENT_SECRET={{google client secret}}
- Clowder configurations (Optional)
  - CLOWDER_BASE_URL={{clowder instance base url}}
  - CLOWDER_GLOBAL_KEY={{clowder global key}}
  - CLOWDER_ON=false (enable connection to clowder or not)

## Past Version History of major SMM analytics components
- [AutoPhrase](./rabbitmq/autophrase/version.md)
- [Classification Spit](./rabbitmq/classification_split/version.md)
- [Classification Train](./rabbitmq/classification_train/version.md)
- [Classification Predict](./rabbitmq/classification_predict/version.md)
- [Named Entity Recognition](./rabbitmq/name_entity_recognition/version.md)
- [Network Analysis](./rabbitmq/network_analysis/version.md)
- [Sentiment Analysis](./rabbitmq/sentiment_analysis/version.md)
- [Topic Modeling](./rabbitmq/topic_modeling/version.md)
- [Preprocessing](./rabbitmq/preprocessing/version.md)

## Contributions
We welcome contributions from the community to enhance and expand our analytics features. Whether you're an experienced
data scientist or just starting in the field, your insights and contributions can help drive innovation in
social media research.  

## Contact Us
- For more information, visit [Social Media Macroscope](https://smm.ncsa.illinois.edu/).
- Contact us the if you have any questions: <a href="mailto:smm@lists.illinois.edu">smm@lists.illinois.edu</a>
