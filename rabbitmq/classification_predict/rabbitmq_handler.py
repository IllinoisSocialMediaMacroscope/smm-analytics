import json
import os
import traceback

import pika
import writeToS3 as s3
from lambda_classification_predict import Classification
import postToAWSLambda

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')

def rabbitmq_handler(ch, method, properties, body):
    try:
        msg = {}

        # determine if it goes to aws, lambda, or batch
        params = json.loads(body)

        if params['platform'] == 'aws-lambda':
            msg = postToAWSLambda.invoke(params['function_name'], params)
            ch.basic_publish(exchange="",
                             routing_key=properties.reply_to,
                             properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                             body=json.dumps(msg))

        elif params['platform'] == 'aws-batch':
            raise ValueError("Not applicable to aws-batch")

        elif params['platform'] == 'lambda':
            event = json.loads(body)

            uid = event['uid']
            awsPath = event['s3FolderName'] + '/ML/classification/' + uid + '/'
            localSavePath = '/tmp/' + event['s3FolderName'] + '/ML/classification/' + uid + '/'
            if not os.path.exists(localSavePath):
                os.makedirs(localSavePath)
            if not os.path.exists(localSavePath):
                os.makedirs(localSavePath)

            # download config to local folder
            fname_config = 'config.json'
            try:
                s3.downloadToDisk(fname_config, localSavePath, awsPath)
                with open(localSavePath + fname_config, "r") as fp:
                    data = json.load(fp)
                    for key in data.keys():
                        if key not in event.keys():
                            event[key] = data[key]
                with open(localSavePath + fname_config, "w") as f:
                    json.dump(event, f)
                s3.upload(localSavePath, awsPath, fname_config)
                msg['config'] = s3.generate_downloads(awsPath, fname_config)
                msg['uid'] = uid

            except:
                raise ValueError('This session ID is invalid!')

            # download unlabeled data to local folder
            fname_unlabeled = 'testing.csv'
            try:
                s3.downloadToDisk(fname_unlabeled, localSavePath, awsPath)
            except:
                raise ValueError('You\'re requesting ' + fname_unlabeled + ' file, and it\'s not found in your remote directory!\
                            It is likely that you have not yet performed step 1 -- split the dataset into training and predicting set, or you have provided the wrong sessionID.')

            # download pickle model to local folder
            fname_pickle = 'pipeline.pickle'
            try:
                s3.downloadToDisk(fname_pickle, localSavePath, awsPath)
            except:
                raise ValueError('You\'re requesting ' + fname_pickle + ' file, and it\'s not found in your remote directory! \
                            It is likely that you have not yet performed step 2 -- model training, or you have provided the wrong sessionID.')

            classification = Classification(awsPath, localSavePath)
            msg['predicting'] = classification.predict()
            msg['div_category'] = classification.plot()

            ch.basic_publish(exchange="",
                             routing_key=properties.reply_to,
                             properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                             body=json.dumps(msg))

        elif params['platform'] == 'batch':
            raise ValueError("Not applicable to aws-batch")

        else:
            raise ValueError(
                'Rabbitmq Message Not Recognizable. '
                'It has to specify what platform to run: aws-lambda, aws-batch, lambda or batch.')

    except BaseException as e:

        msg = {'ERROR':
                   {'message': str(e),
                    'traceback': traceback.format_exc()
                    }
               }

        # reply to the sender
        ch.basic_publish(exchange="",
                         routing_key=properties.reply_to,
                         properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                         body=json.dumps(msg))

    return msg


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(port=5672, host=RABBITMQ_HOST))
    channel = connection.channel()

    # pass the queue name in environment variable
    queue = os.environ['QUEUE_NAME']

    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=rabbitmq_handler, auto_ack=True)
    channel.start_consuming()
