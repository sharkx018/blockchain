from time import time
from oop.printable import Printable

class Block(Printable):
    def __init__(self, index, previous_hash, transactions, proof, timezone=None):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof = proof
        self.timestamp = time() if timezone is None else timezone
