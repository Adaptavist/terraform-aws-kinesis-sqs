import unittest
import hashlib
import json
import logging
import sys

# =============SET LOGGING=====================================
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('Loading function')
# =============================================================
class TestRecordProcessing(unittest.TestCase):
    def setUp(self):
        self.input_record = {
            "path": "/data-extraction/path",
            "payload": {
                "path": "/data-extraction",
                "payload": {
                "type": "message",
                "id": "2410081",
                "href": "/messages/2410081",
                "view_href": "https:",
                "author": {
                    "type": "user",
                    "id": "2467514",
                    "href": "/users/2467514",
                    "view_href": "https:",
                    "login": "baguss"
                }
                }
            }
            }
        self.keys = 'path'
        self.keys_list = 'payload,payload,id'
        self.key_to_hash = "/data-extraction/path"
        self.hash_one = hashlib.md5(self.key_to_hash.encode()).hexdigest()
        self.hash_none = hashlib.md5(json.dumps(self.input_record, sort_keys=True).encode()).hexdigest()
    
    def test_extract_keys(self):
        extract = extract_keys(self.input_record, self.keys.split(','))
        assert extract == "/data-extraction/path"
    
    def test_extract_keys_list(self):
        extract = extract_keys(self.input_record, self.keys_list.split(','))
        assert extract == "2410081"
    
    def test_extract_keys_none(self):
        extract = extract_keys(data=self.input_record)
        assert extract == 'No key provided'
    
    def test_create_hash_key(self):
        hash = create_hash_key(self.input_record,self.keys)
        assert hash == self.hash_one

    def test_create_hash_key_none(self):
        hash = create_hash_key(data=self.input_record)
        assert hash == self.hash_none

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

if __name__ == '__main__':
    unittest.main()
