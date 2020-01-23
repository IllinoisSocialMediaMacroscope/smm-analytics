import boto3
import os

client = boto3.client('batch', region_name="us-west-2", aws_access_key_id = os.environ['AWS_ACCESSKEY'],
                      aws_secret_access_key = os.environ['AWS_ACCESSKEYSECRET'])

def invoke(jobDefinition, jobName, jobQueue, command):
    response = client.submit_job(
        jobDefinition=jobDefinition,
        jobName=jobName,
        jobQueue=jobQueue,
        containerOverrides={
            'vcpus': 2,
            'memory': 2048,
            'command': command
        }
    )

    return response