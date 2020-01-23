import json
import boto3
import os

client = boto3.client('lambda', region_name="us-west-2", aws_access_key_id = os.environ['AWS_ACCESSKEY'],
                      aws_secret_access_key = os.environ['AWS_ACCESSKEYSECRET'])

def invoke(function_name, args):
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