import os
import logging
import boto3
import base64
import json
from redis import Redis
import hashlib
import sys
import uuid

# =============SET ENVIRONMENT VARIABLES=======================
sqs = boto3.client('sqs')
queue_url = os.environ.get('SQS_QUEUE_URL')
is_fifo_queue = os.environ.get('IS_FIFO_QUEUE')
# ==============================================================
data_primary_key = os.environ.get('DATA_PRIMARY_KEY', '')
redis_key = os.environ.get('REDIS_HASH_KEY', '')
host=os.environ.get('HOST','host')
redis = Redis(host=host, port=6379)
path_value_filter = os.environ.get('PATH_VALUE_FILTER','/hubspot-consumer/events/salable')
# =============================================================
# =============SET LOGGING=====================================
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('Loading function')
if queue_url:
    logger.info("Queue url : " + queue_url)
# =============================================================


def replace_none_values(data: dict) -> dict:
    """
    Replace None values in data with empty strings.

    Parameters:
        data (dict): The data to remove none values from

    Returns:
        A dictionary containing the cleaned data
    """
    return {key: ('' if value is None else value) for key, value in data.items()}


def lambda_handler(event: dict) -> None:
    """
        Handles the event from the kinesis stream

        Parameters:
            event (dict): The kinesis event
            context: LambdaContext
    """
    
    logger.info(event)
    
    for record in event['Records']:
        dataBase64 = record['kinesis']['data']
        dataJson = base64.b64decode(dataBase64)
        data = json.loads(dataJson)
        print(data)
        print(data.get('path'))
        '''
        The below enables multiple consumers to optionally leverage Redis based on configuration 
        and specific record attributes.
        
        If just the Redis connection is set, send all records via Redis calling replace_none_values
    
        If path_value_filter is set, only records matching the path_value_filter should be sent to Redis 
        calling replace_none_values, others should be sent directly to SQS
        '''

        if redis.connection_pool.connection_kwargs['host']:
            send_to_redis = False

            if path_value_filter:
                if data.get('path') == path_value_filter:
                    send_to_redis = True
            else:
                # No path_value_filter, all data to go via Redis
                send_to_redis = True
            
            if send_to_redis:
                data = replace_none_values(data)
                print(f'cleaned data -> {data}')
                print('send to redis')
            else:
                print('send to sqsq')
        else:
            print('send to sqs')


data={
            "path": "/data-extraction/path",
            "first_none": None,
            "payload": {
                "path": "/data-extraction",
                "second_none": None,
                "payload": {
                "third_none": None,
                "type": "message",
                "id": "2410081",
                "href": "/messages/2410081",
                "view_href": "https:",
                "author": {
                    "type": "user",
                    "fourth_none": None,
                    "id": "2467514",
                    "href": "/users/2467514",
                    "view_href": "https:",
                    "login": "baguss"
                },
                "fifth_none": None,
                }
            }
            }


def replace_none_values(data: dict):
    """
    Recursively replace None values from a dictionary.

    Parameters:
        data (dict): The dictionary to process.

    Returns:
        A new dictionary with None values removed.
    """
    for key, value in list(data.items()):
        if value is None:
            data[key] = ''
        elif isinstance(value, dict):
            # Recurse into nested dictionaries
            replace_none_values(value) 
    return data

# values = replace_none_values(data=data)
print(f"first_none: {data['first_none']}")
print(f"second_none: {data['payload']['second_none']}")
print(f"third_none: {data['payload']['payload']['third_none']}")
print(f"fourth_none: {data['payload']['payload']['author']['fourth_none']}")
print(f"fifth_none: {data['payload']['payload']['fifth_none']}")

if data['first_none'] == '':
    print('balnk value')
else:
    print('none value')