import os
import logging
import boto3
import base64
import json
from redis import Redis
import hashlib

# =============SET LOGGING=====================================
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('Loading function')
# =============================================================
# =============SET ENVIRONMENT VARIABLES=======================
sqs = boto3.client('sqs')
queue_url = os.environ.get('SQS_QUEUE_URL')
is_fifo_queue = os.environ.get('IS_FIFO_QUEUE')
logger.info("Queue url : " + queue_url)
data_primary_key = os.environ.get('DATA_PRIMARY_KEY', '')
redis_hash_key = os.environ.get('REDIS_HASH_KEY','')
host=os.environ.get('HOST','')
redis = Redis(host=host, port=6379)
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
      
        # if a redis connection has been set then process data accordingly
        if redis.connection_pool.connection_kwargs['host']:
            logger.info('removing NULLs for redis')
            # redis doesn't like null values so replace them with empty strings
            for key, value in data.items():
                if value is None:
                    data[key] = ''

            # send data to redis
            data_to_redis(payload=data, data_base_64=dataBase64)
        else:
            send_to_sqs(data=data, message_body=json.dumps(data), data_base_64=dataBase64)
    


def data_to_redis(payload: dict, data_base_64: str) -> None:
    """
        Takes in the processed data from the lambda_handler,
        creates a unique hash key of the record which determines whether it
        should be added to the Redis cluster and then sent to the SQS queue
    
        Parameters:
            payload (dict): The veniture license record
            data_base_64 (str): dataBase64 variable from the lambda_handler to be passed to the send_to_sqs function
    """

    key = extract_keys(payload, redis_hash_key)
    try:
        if key:
            hash_key = hashlib.md5(key.encode()).hexdigest()
        else:
            hash_key = hashlib.md5(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        if redis.hsetnx('records', hash_key, json.dumps(payload)):
            logger.info(f"New record with hash key '{hash_key}' added to hash 'records'")
            logger.info(f'Sending {payload} to SQS')
            
            # Send record to SQS queue
            message_body = json.dumps(payload)
            send_to_sqs(payload, message_body, data_base_64)
        else:
            (f"Record with hash key '{hash_key}' already exists in hash 'records'")
    except Exception as e:
        logger.info(f'Problem sending data to the redis cluster / SQS {e}')

def send_to_sqs(data: dict, message_body: str, data_base_64: str) -> None:
    """
        Takes the data proccessed from the lambda_handler and sends it to the SQS queue
    
        Parameters:
            data (dict): The payload to be sent to SQS
            message_body (str): Contents of the payload
            data_base_64 (str): dataBase64 variable from the lambda_handler to be passed to the send_to_sqs function
    """

    groupId = ""
    if data[data_primary_key]:
        groupId = data[data_primary_key]
        logger.info(groupId)
    else:
        groupId = data_base_64

    sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body,
            MessageDeduplicationId=data_base_64,
            MessageGroupId=groupId)  


def extract_keys(data:dict, keys: list) -> str:
    """
    Takes in a dict object and a key list.
    Loops through the data extracting the specified key

    Parameters:
        data (dict): The data to be iterated over
        keys (list): List of keys to get required value from data

    Returns:
        A dictionary containing the created ticket information
    """
    
    try:
        if keys:
            extract = data
            for key in keys:
                if key in extract:
                    extract = extract[key]
                else:
                    break     
    except Exception as e:
        logger.info(f'problem extracting the key value {e}')
    return str(extract)  











