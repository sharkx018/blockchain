import json
from utility.hash_util import hash_block
from block import Block
from transactions import Transactions
from utility.verfication import Verification

# Mining Config
MINING_REWARD = 10
MINING = 'MINING'

class Blockchain:
    def __init__(self, hosting_node_id):
        # Starting block of the blockchain
        genesis_block = Block(0, '', [], 100, 0)
        # Init the blockchain list
        self.__chain = [genesis_block]
        # Unhandled Transactions
        self.__open_transactions = []
        self.load_data()
        self.hosting_node_id = hosting_node_id

    def get_chain(self):
        return self.__chain[:]

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with open('blockchain.txt', mode='r') as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [
                        Transactions(tx['sender'],
                                     tx['recipient'],
                                     tx['amount'])
                        for tx in block['transactions']
                    ]

                    updated_block = Block(
                        block['index'],
                        block['previous_hash'],
                        converted_tx,
                        block['proof'],
                        block['timestamp']
                    )
                    updated_blockchain.append(updated_block)
                self.__chain = updated_blockchain
                self.__open_transactions = json.loads(file_content[1])

                updated_open_transactions = []
                for open_tx in self.__open_transactions:
                    updated_open_tx = Transactions(
                        open_tx['sender'],
                        open_tx['recipient'],
                        open_tx['amount']
                    )
                    updated_open_transactions.append(updated_open_tx)
                self.__open_transactions = updated_open_transactions
        except:
            print('Handled Exception...')
        finally:
            print('Cleanup!')

    def save_data(self):
        try:
            with open('blockchain.txt', mode='w') as f:

                savable_chain = [block.__dict__.copy() for block in [
                    Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions],
                          block_el.proof, block_el.timestamp) for block_el in self.__chain]]

                f.write(json.dumps(savable_chain))
                f.write('\n')
                savable_transactions = [open_tx.__dict__.copy() for open_tx in self.__open_transactions]
                f.write(json.dumps(savable_transactions))
        except IOError:
            print('Error: File not saved!')

    def proof_of_work(self):
        last_block = self.__chain[-1]
        lash_block_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, lash_block_hash, proof):
            proof += 1

        return proof

    def get_balance(self):
        participant = self.hosting_node_id

        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]
        open_transaction_sender_amount = [open_tx.amount for open_tx in self.__open_transactions if
                                          open_tx.sender == participant]
        tx_sender.append(open_transaction_sender_amount)

        tx_send_amount = 0
        for tx in tx_sender:
            for amount_sent in tx:
                tx_send_amount += amount_sent

        tx_receiver = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in
                       self.__chain]
        tx_receive_amount = 0
        for tx in tx_receiver:
            for amount_received in tx:
                tx_receive_amount += amount_received

        return tx_receive_amount - tx_send_amount

    def get_last_blockchain_value(self):
        """ Returns the last value of current blockchain. """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient, sender, amount=1.0):
        transaction = Transactions(
            sender,
            recipient,
            amount
        )

        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True

        return False

    def mine_block(self):
        last_block = self.__chain[-1]

        hashed_block = hash_block(last_block)
        print("====>>>>>Hashed Block:", hashed_block)

        proof = self.proof_of_work()

        # Mining Reward

        reward_transaction = Transactions(
            MINING,
            self.hosting_node_id,
            MINING_REWARD
        )

        # open_transactions.append(reward_transaction)
        copied_transaction = self.__open_transactions[:]
        copied_transaction.append(reward_transaction)

        block = Block(
            len(self.__chain),
            hashed_block,
            copied_transaction,
            proof,
        )

        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return True
