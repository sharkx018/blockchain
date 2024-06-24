import hashlib as hl
import json


def hash_string(string: str):
    encoded_payload = string.encode()
    return hl.sha256(encoded_payload).hexdigest()


def hash_block(block):
    hashable_block = block.__dict__.copy()
    return hash_string(json.dumps(hashable_block, sort_keys=True))
