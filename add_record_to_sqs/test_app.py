import unittest
from app import extract_keys
from app import create_hash_key
import hashlib
import json


class TestRecordProcessing(unittest.TestCase):
    def setUp(self):
        self.input_record = {
            'type': 'create',
            'email': 'example@example.com',
            'first_name': 'FN',
            'last_name': 'LN',
            'sent_timestamp': '2023-06-08T07:56:04+00:00',
            'account_create_timestamp': '2023-06-08T07:56:04.316+00:00'
        }
        self.keys = ['type']
        self.key_str= 'type'
        self.key_to_hash = 'create'
        self.hash_one = hashlib.md5(self.key_to_hash.encode()).hexdigest()
        self.hash_none = hashlib.md5(json.dumps(self.input_record, sort_keys=True).encode()).hexdigest()
    
    def test_extract_keys(self):
        extract = extract_keys(self.input_record, self.keys)
        assert extract == 'create'
      
    
    def test_extract_keys_none(self):
        extract = extract_keys(data=self.input_record)
        assert extract == 'No key provided'
    
    
    def test_create_hash_key(self):
        hash = create_hash_key(self.input_record,self.key_str)
        assert hash == self.hash_one

    def test_create_hash_key_none(self):
        hash = create_hash_key(data=self.input_record)
        assert hash == self.hash_none

if __name__ == '__main__':
    unittest.main()

