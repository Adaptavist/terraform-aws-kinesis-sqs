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
path_value_filter = os.environ.get('PATH_KEY','/hubspot-consumer/events/talentlms')
host=os.environ.get('HOST','host')
redis = Redis(host=host, port=6379)

# If connection set use redis
# if key set use that to hash on, if no key take the entire record

# if a conncetion is set and a path filter just the path records go to redis
def lambda_handler_two(event: dict) -> None:
    """
        Handles the event from the kinesis stream

        Parameters:
            event (dict): The kinesis event
            context: LambdaContext
    """
    
    print(event)
    
    for record in event['Records']:
        dataBase64 = record['kinesis']['data']
        dataJson = base64.b64decode(dataBase64)
        data = json.loads(dataJson)
        print(data['path'])

        # if a redis connection has been set then process data accordingly
        # if 
        if path_value_filter and redis.connection_pool.connection_kwargs['host']:
            # just send certain records to redis
            if data['path'] == path_value_filter: 
                # redis doesn't like null values so replace them with empty strings
                for key, value in data.items():
                    if value is None:
                        data[key] = ''

            # send data to redis
            print('send to redis')
        else:
            print('send to sqs')

file = 'test.json'
event = json.load(open(file, 'r'))
lambda_handler_two(event)