import hashlib as hl
import json


def hash_string(string: str):
    encoded_payload = string.encode()
    return hl.sha256(encoded_payload).hexdigest()


def hash_block(block):
    return hash_string(json.dumps(block, sort_keys=True))
