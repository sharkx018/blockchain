import hashlib as hl
import json


def hash_string(string: str):
    encoded_payload = string.encode()
    return hl.sha256(encoded_payload).hexdigest()


def hash_block(block):
    # block.transactions = [tx.to_ordered_dict() for tx in block.transactions]
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    return hash_string(json.dumps(hashable_block, sort_keys=True))
