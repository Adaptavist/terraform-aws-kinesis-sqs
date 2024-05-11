import os
import logging
import boto3
import base64
import json
# from redis import Redis
import hashlib
import sys
import uuid
from dotenv import load_dotenv
load_dotenv()

# =============SET ENVIRONMENT VARIABLES=======================
SQS_REGION = os.environ.get('SQS_REGION')
QUEUE_URL = os.environ.get('SQS_QUEUE_URL')
IS_FIFO_QUEUE = os.environ.get('IS_FIFO_QUEUE')
# ==============================================================
HOST = os.environ.get('HOST','some-url')
PORT=6379
PATH_VALUE_FILTER = os.environ.get('PATH_VALUE_FILTER','')
# =============================================================
# ===TEST CONFIG VALUE=========================================
config_str = os.getenv('CONFIG')
 # Parse the JSON string back into a Python list
if config_str:
    config = json.loads(config_str)
else:
    config = []
print(config)
# =============================================================
# =============SET LOGGING=====================================
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('Loading function')
if QUEUE_URL:
    logger.info("Queue url : %s", QUEUE_URL)
# =============================================================

class SqsUtils:
    """
    Contains methods for interacting with boto3 SQS client and the redis client
    """
    def __init__(self):
        boto3.setup_default_session(region_name=SQS_REGION)
        self._client = boto3.client('sqs')
        # self._redis = Redis(host=HOST, port=PORT)

    def data_to_redis_to_sqs(self, payload: dict, config: dict = None) -> None:
        """
            Takes in the processed data from the lambda_handler,
            creates a unique hash key of the record which determines whether it
            should be added to the Redis cluster and then sent to the SQS queue
        
            Parameters: 
                payload (dict): The record to be sent
        """
        REDIS_KEY = config["redis_hash_keys"] 
        hash_key = create_hash_key(data=payload, keys=REDIS_KEY)
        print(f'hash_key created {hash_key}')
        # try:
        #     if self._redis.hsetnx('records', hash_key, json.dumps(payload)):
        #         logger.info("New record with hash key '%s' added to hash 'records'", hash_key)
        #         logger.info('Sending %s to SQS', payload)

        #         # Send record to SQS queue
        #         message_body = json.dumps(payload)
        #         self.send_to_sqs(payload, message_body)
        #     else:
        #         logger.info("Record with hash key '%s' already exists in hash 'records'", hash_key)
        # except Exception as e:
        #     logger.info('Problem sending data to the redis cluster / SQS %s', e)

    def send_to_sqs(self, data: dict, message_body: str, config: dict = None) -> None:
        """
            Takes the data proccessed from the lambda_handler and sends it to the SQS queue
        
            Parameters:
                data (dict): The payload to be sent to SQS
                message_body (str): Contents of the payload
                data_base_64: 
        """
        DATA_PRIMARY_KEY = config["data_primary_key"]
        # If redis is used take a UUID else use a HASH
        if HOST:
            message_deduplication_id = str(uuid.uuid4())
        else:
            # Generate the hash-based MessageDeduplicationId
            message_deduplication_id = hashlib.md5(
                json.dumps(data, sort_keys=True).encode()
            ).hexdigest()

        if DATA_PRIMARY_KEY:
            try:
                # Call the extract_keys function to get the value for groupId from the data
                extract_value = extract_keys(data, DATA_PRIMARY_KEY.split(','))
                print(f'extract_value: {extract_value}')
                group_id = str(extract_value)
            except Exception as e:
                raise Exception(f'Problem occurred with data_primary_key: {e}')
        else:
            group_id = message_deduplication_id

        print(f'sending to sqs: {message_body}')
        # self._client.send_message(
        #         QueueUrl=QUEUE_URL,
        #         MessageBody=message_body,
        #         MessageDeduplicationId=message_deduplication_id,
        #         MessageGroupId=group_id)

    # def redis_host(self):
    #     """returns the hostname of redis"""
    #     return self._redis.connection_pool.connection_kwargs['host']


def lambda_handler(event: dict) -> None:
    """
        Handles the event from the kinesis stream

        Parameters:
            event (dict): The kinesis event
            context: LambdaContext
    """

    # logger.info(event)
    sqs = SqsUtils()

    for record in event['Records']:
        data_base_64 = record['kinesis']['data']
        data_json = base64.b64decode(data_base_64)
        data = json.loads(data_json)
        print('processing data')
        # print(data)

        '''
        The below enables multiple consumers to optionally leverage Redis based on configuration 
        and specific record attributes.
        
        If just the Redis connection is set, send all records via Redis calling replace_none_values
    
        If path_value_filter is set, only records matching the path_value_filter should be sent to Redis 
        calling replace_none_values, others should be sent directly to SQS
        '''

        # Iterate through each config to find a matching path_value_filter
        for cfg in config:
            if HOST and (data.get('path') == cfg["path_value_filter"] or cfg["path_value_filter"] == ""):
                print('1: replace_none_values')
                data = replace_none_values(data)
                # print(f'2: data_to_redis_to_sqs.. {data}')
                sqs.data_to_redis_to_sqs(payload=data, config=cfg)
            else:
                print('1: send_to_sqs')


def extract_keys(data: dict, keys: list | None = None) -> str:
    """
    Takes in a dict object and a list of composite keys.
    Loops through the data extracting the specified key values and concatenates them.

    Parameters:
        data (dict): The data to be iterated over
        keys (list): List of composite keys to get required values from data (optional)

    Returns:
        The concatenated value of the composite keys provided
    """
    print(f'calling extract_keys, working with keys {keys}')
    extracted_values = []
    try:
        if keys is not None:
            for full_key in keys:
                # Split each key by the comma to handle composite keys
                subkeys = full_key.split(',')
                extract = data
                for key in subkeys:
                    if key in extract:
                        print(f'found key: {key}')
                        extract = extract[key]
                    else:
                        # If any key in the sequence does not exist, break and move to the next full_key
                        extract = None
                        break
                if extract is not None:
                    extracted_values.append(str(extract))
        else:
            return 'No key provided'
    except Exception as e:
        logger.fatal(f'Problem occurred extract_keys: {e} terminating the process')
        sys.exit(1)
    return ''.join(extracted_values)

# # Example usage:
# data = {
#     "payload": {
#         "id": "123",
#         "email": "example@example.com"
#     }
# }
# keys = ['payload,id', 'payload,email']
# print(extract_keys(data, keys))

def create_hash_key(data:dict, keys: list | None = None) -> str:
    """
    Takes a specified key from the env vars. Returns a hash based on either this key or the entire record

    Parameters:
        data (dict): The record processed from the kinesis stream
        key (str): The key to create a hash on (optional)

    Returns:
        A hash key to define a distinct record to send to redis
    """
    print(f'calling create_hash_key, working with... {data}')
    try:
        if keys is not None:
            new_key = extract_keys(data, keys)
            print(f'got new_key: {new_key}')
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


event = json.load(open('test-kinesis-three.json', 'r'))

lambda_handler(event=event)