import json
import boto3
import os

client = boto3.client('lambda', region_name="us-west-2", aws_access_key_id = os.environ['AWS_ACCESSKEY'],
                      aws_secret_access_key = os.environ['AWS_ACCESSKEYSECRET'])

def invoke(function_name, args):

    # pass information so remote lambda can access local s3 minio
    args['HOST_IP'] = os.environ['MINIOURL']
    args['AWS_ACCESSKEY'] = os.environ['AWS_ACCESSKEY']
    args['AWS_ACCESSKEYSECRET'] = os.environ['AWS_ACCESSKEYSECRET']
    args['BUCKET_NAME'] = os.environ['BUCKET_NAME']

    response = client.invoke(
        Payload=json.dumps(args),
        FunctionName=function_name,
        InvocationType='RequestResponse',
        LogType='Tail',
    )

    if response['StatusCode'] == 200:
        results = json.loads(response['Payload'].read().decode('utf-8'))
    else:
        results = {'ERROR': response['FunctionError']}

    return results