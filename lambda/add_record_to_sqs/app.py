import os
import logging
import boto3
import base64
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('Loading function')

sqs = boto3.client('sqs')
queue_url = os.environ.get('SQS_QUEUE_URL')
is_fifo_queue = os.environ.get('IS_FIFO_QUEUE')
logger.info("Queue url : " + queue_url)
data_primary_key = os.environ.get('DATA_PRIMARY_KEY')

def lambda_handler(event, context):

    logger.info(event)

    for record in event['Records']:
        dataBase64 = record['kinesis']['data']
        dataJson = base64.b64decode(dataBase64)
        data = json.loads(dataJson)
        logger.info(data)

        if data_primary_key in data:
            dedupKey = data[data_primary_key] + data['type'] + data['sent_timestamp']
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=dataJson.decode("utf-8"),
                MessageDeduplicationId=dedupKey,
                MessageGroupId=data[data_primary_key]
            )
        else:
            logger.error(f'NO ${data_primary_key} sPROPERTY IN MESSAGE!')











