import os
import logging
import boto3
import base64
import json
from redis import Redis
import hashlib

# =============SET ENVIRONMENT VARIABLES=======================
sqs = boto3.client('sqs')
queue_url = os.environ.get('SQS_QUEUE_URL')
is_fifo_queue = os.environ.get('IS_FIFO_QUEUE')
host=os.environ.get('HOST','')
# =============================================================
# =============SET LOGGING=====================================
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('Loading function')
logger.info("Queue url : " + queue_url)
# =============================================================

def lambda_handler(event: dict, context) -> None:
    """
        Handles the kinesis event from the ingest-veniture-licenses-events stream,
        makes a test connection to the redis cluster and then processes the data 
        and passes it to the data_to_redis function

        Parameters:
            event (dict): The kinesis event
            context: LambdaContext
    """
    
    logger.info(event)

    for record in event['Records']:
        dataBase64 = record['kinesis']['data']
        dataJson = base64.b64decode(dataBase64)
        data = json.loads(dataJson)
        logger.info(data)
        
        # redis doesn't like null values so replace them with empty strings
        for key, value in data.items():
            if value is None:
                data[key] = ''

        # remove created_at from payload as this is a value we create
        data.pop('created_at')
        
        # call data load function
        data_to_redis(payload=data,conn=test_redis_conn())

def test_redis_conn() -> Redis:
    """
        Makes a test connection to the redis cluster returns the Redis connection object 
        that stores the credentials
           
           Returns:
            <class 'redis.client.Redis'> 
    """
    redis = Redis(host=host, port=6379)
    try:
        if redis.ping():
            logger.info("Connected to Redis")
        else:
            logger.info('Not connected to Redis')
        return redis
    except Exception as e:
        logger.error(f'problem connecting to Redis: {e}')

def data_to_redis(payload: dict, conn: Redis) -> None:
    """
        Takes in the processed data from the lambda_handler,
        creates a unique hash key of the record which determines whether it
        should be added to the Redis cluster and then sent to the SQS queue
    
        Parameters:
            payload (dict): The veniture license record
            conn (<class 'redis.client.Redis'>): Redis connection object that stores the credentials
    """
    
    try:
        hash_key = hashlib.md5(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        if conn.hsetnx('records', hash_key, json.dumps(payload)):
            logger.info(f"New record with hash key '{hash_key}' added to hash 'records'")
            logger.info(f'Sending {payload} to SQS')
            
            # Send record to SQS queue
            message_body = json.dumps(payload)
            send_to_sqs(payload, message_body)
            count_redis_records()
        else:
            logger.info(f"Record with hash key '{hash_key}' already exists in hash 'records'")
            # print('deleteing records')
            # conn.delete('records')
    except Exception as e:
        logger.error(f'Problem sending data to the redis cluster / SQS {e}')

def send_to_sqs(data: dict, message_body: str) -> None:
    """
        Takes the data proccessed from the lambda_handler and sends it to the SQS queue
    
        Parameters:
            data (dict)): The ticket name / summary
            message_body (str): The ticket description
    """
             
    if data['license_id']:
        dedupKey = str(data['license_id']) + str(data['sen'])
        logger.info(f'dedupKey: {dedupKey}')
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body,
            MessageDeduplicationId=dedupKey,
            MessageGroupId=str(data['license_id'])
        )
        logger.info('SQS message sent')
    else:
        logger.error('Issue occured when sending message to SQS')

def count_redis_records():
        """
        Counts the number of redis records added
        """
        redis = test_redis_conn()
        count = redis.hlen('records')
        logger.info(f'Records: {count}')
    














