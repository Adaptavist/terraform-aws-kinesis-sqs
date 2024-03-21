import os
import logging
import boto3
import base64
import json
from redis import Redis
import hashlib
import sys
import uuid

data_primary_key = os.environ.get('DATA_PRIMARY_KEY', '')
redis_key = os.environ.get('REDIS_HASH_KEY', '')
path_value_filter = os.environ.get('PATH_KEY','/hubspot-consumer/events/salable')
host=os.environ.get('HOST','host')
redis = Redis(host=host, port=6379)



def replace_none_values(data: dict) -> dict:
    """
    Replace None values in data with empty strings.

    Parameters:
        data (dict): The data to remove none values from

    Returns:
        A dictionary containing the cleaned data
    """
    return {key: ('' if value is None else value) for key, value in data.items()}

def lambda_handler_two(event: dict) -> None:
    """
        Handles the event from the kinesis stream

        Parameters:
            event (dict): The kinesis event
            context: LambdaContext
    """
    
    has_redis_connection = redis.connection_pool.connection_kwargs['host']
    # print(event)
   
    for record in event['Records']:
        dataBase64 = record['kinesis']['data']
        dataJson = base64.b64decode(dataBase64)
        data = json.loads(dataJson)
        print(data['path'])

        if has_redis_connection:
            data = replace_none_values(data)
        
        if has_redis_connection:
            # If path_value_filter is set, decide based on the path
            if path_value_filter:
                if data.get('path') and data.get('path') != path_value_filter:
                    print('send to sqs')
                else:
                 print('send to redis')
        else:
            print('send to sqs')

file = 'test.json'
event = json.load(open(file, 'r'))
lambda_handler_two(event)
