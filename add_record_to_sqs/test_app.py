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
    
    def test_replace_nonce_values(self):
        data = replace_none_values(data=self.input_record)
        assert data['first_none'] == ''
        assert data['payload']['second_none'] == ''
        assert data['payload']['payload']['third_none'] == ''
        assert data['payload']['payload']['author']['fourth_none'] == ''


def extract_keys(data:dict, keys: list|None = None) -> str:
    """
    Takes in a dict object and a list of composite keys.
    Loops through the data extracting the specified key values and concatenates them.

    Parameters:
        data (dict): The data to be iterated over
        keys (list): List of composite keys to get required values from data (optional)

    Returns:
        The concatenated value of the composite keys provided
    """
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
        logger.error(f'Problem occurred extract_keys: {e}')
    return ''.join(extracted_values) 

def create_hash_key(data:dict, keys: list | None = None) -> str:
    """
    Takes a specified key from the env vars. Returns a hash based on either this key or the entire record

    Parameters:
        data (dict): The record processed from the kinesis stream
        keys (list): The keys to create a hash on (optional)

    Returns:
        A hash key to define a distinct record to send to redis
    """
    try:
        if keys is not None:
            new_key = extract_keys(data, keys)
            hash_key = hashlib.md5(new_key.encode()).hexdigest()
        else:
            hash_key = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    except Exception as e:
        logger.error(f'Problem occurred create_hash_key: {e}')
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


if __name__ == '__main__':
    unittest.main()
