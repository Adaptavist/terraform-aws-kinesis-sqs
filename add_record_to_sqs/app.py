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
host=os.environ.get('HOST','')
redis = Redis(host=host, port=6379)
path_value_filter = os.environ.get('PATH_VALUE_FILTER','')
# =============================================================
# =============SET LOGGING=====================================
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('Loading function')
if queue_url:
    logger.info("Queue url : " + queue_url)
# =============================================================


def lambda_handler(event: dict, context) -> None:
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
                # No path_value_filter + redis connection -> all data to go via Redis
                send_to_redis = True
            
            if send_to_redis:
                data = replace_none_values(data)
                data_to_redis_to_sqs(payload=data)
            else:
                send_to_sqs(data=data, message_body=json.dumps(data))
        else:
            send_to_sqs(data=data, message_body=json.dumps(data))


def data_to_redis_to_sqs(payload: dict) -> None:
    """
        Takes in the processed data from the lambda_handler,
        creates a unique hash key of the record which determines whether it
        should be added to the Redis cluster and then sent to the SQS queue
    
        Parameters:
            payload (dict): The record to be sent
    """

    hash_key = create_hash_key(data=payload, key=redis_key)
    try:
        if redis.hsetnx('records', hash_key, json.dumps(payload)):
            logger.info(f"New record with hash key '{hash_key}' added to hash 'records'")
            logger.info(f'Sending {payload} to SQS')
            
            # Send record to SQS queue
            message_body = json.dumps(payload)
            send_to_sqs(payload, message_body)
        else:
            logger.info(f"Record with hash key '{hash_key}' already exists in hash 'records'")
    except Exception as e:
        logger.info(f'Problem sending data to the redis cluster / SQS {e}')

def send_to_sqs(data: dict, message_body: str) -> None:
    """
        Takes the data proccessed from the lambda_handler and sends it to the SQS queue
    
        Parameters:
            data (dict): The payload to be sent to SQS
            message_body (str): Contents of the payload
            data_base_64: 
    """
    
    # If redis is used take a UUID else use a HASH
    if redis.connection_pool.connection_kwargs['host']:
        message_deduplication_id = str(uuid.uuid4())
    else:
        # Generate the hash-based MessageDeduplicationId
        message_deduplication_id = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

    if data_primary_key:
        try:
            # Call the extract_keys function to get the value for groupId from the data
            extract_value = extract_keys(data, data_primary_key.split(','))
            groupId = str(extract_value)
        except Exception as e:
            raise Exception(f'Problem occurred with data_primary_key: {e}')
    else:
        groupId = message_deduplication_id

    sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body,
            MessageDeduplicationId=message_deduplication_id,
            MessageGroupId=groupId)   


def extract_keys(data:dict, keys: list = None) -> str:
    """
    Takes in a dict object and a key list.
    Loops through the data extracting the specified key

    Parameters:
        data (dict): The data to be iterated over
        keys (list): List of keys to get required value from data (optional)

    Returns:
        The value of the key provided
    """
    try:
        if keys is not None:
            extract = data
            for key in keys:
                if key in extract:
                    extract = extract[key]
                else:
                    break 
        else:
            return 'No key provided'
    except Exception as e:
        logger.error(f'Problem occurred extract_keys: {e}')
    return str(extract)  

def create_hash_key(data:dict, key: str = None) -> str:
    """
    Takes a specified key from the env vars. Returns a hash based on either this key or the entire record

    Parameters:
        data (dict): The record processed from the kinesis stream
        key (str): The key to create a hash on (optional)

    Returns:
        A hash key to define a distinct record to send to redis
    """
    try:
        if key is not None:
            redis_hash_key = key.split(",")
            new_key = extract_keys(data, redis_hash_key)
            hash_key = hashlib.md5(new_key.encode()).hexdigest()
        else:
            hash_key = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    except Exception as e:
        logger.fatal(f'Problem occurred create_hash_key: {e} terminating the process')
        sys.exit(1)
    return hash_key

def replace_none_values(data: dict) -> dict:
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
