"""Provide verification helper methods"""

from utility.hash_util import hash_block, hash_string
from wallet import Wallet


class Verification:

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        # guess = (str(tx.to_ordered_dict() for tx in transactions) + str(last_hash) + str(proof))

        tx_str = ''
        for tx in transactions:
            tx_str += str(tx.__dict__)
        guess = str(tx_str) + str(last_hash) + str(proof)

        guess_hash = hash_string(guess)
        return guess_hash[0:2] == '00'

    @classmethod
    def verify_chain(cls, blockchain):
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                print('Blockchain is invalid!')
                print('previous_hash of block is invalid')
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Blockchain is invalid!')
                print('Proof of work is invalid', "info: ", block.transactions[:-1], block.previous_hash, block.proof)
                return False

        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, fund_check=True):
        if fund_check:
            sender_amount = get_balance(transaction.sender)
            return sender_amount >= transaction.amount and Wallet.verify_transaction(transaction)
        else:
            Wallet.verify_transaction(transaction)

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        return all(cls.verify_transaction(tx, get_balance, False) for tx in open_transactions)
