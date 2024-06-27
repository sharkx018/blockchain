import json
from utility.hash_util import hash_block
from block import Block
from transactions import Transactions
from utility.verfication import Verification
from wallet import Wallet
import requests

# Mining Config
MINING_REWARD = 10
MINING = 'MINING'


class Blockchain:
    def __init__(self, public_key, node_id):
        # Starting block of the blockchain
        genesis_block = Block(0, '', [], 100, 0)
        # Init the blockchain list
        self.__chain = [genesis_block]
        # Unhandled Transactions
        self.__open_transactions = []

        self.public_key = public_key
        self.node_id = node_id
        self.__peer_nodes = set()
        self.resolve_conflicts = False

        # Load the blockchain from local storage
        self.load_data()

    def get_chain(self):
        return self.__chain[:]

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with (open('blockchain-{}.txt'.format(self.node_id), mode='r') as f):
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [
                        Transactions(tx['sender'],
                                     tx['recipient'],
                                     tx['signature'],
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
                        open_tx['signature'],
                        open_tx['amount']
                    )
                    updated_open_transactions.append(updated_open_tx)
                self.__open_transactions = updated_open_transactions
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
        except:
            print('Handled Exception...')
        finally:
            print('Cleanup!')

    def save_data(self):
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:

                savable_chain = [block.__dict__.copy() for block in [
                    Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions],
                          block_el.proof, block_el.timestamp) for block_el in self.__chain]]

                f.write(json.dumps(savable_chain))
                f.write('\n')
                savable_transactions = [open_tx.__dict__.copy() for open_tx in self.__open_transactions]
                f.write(json.dumps(savable_transactions))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
        except IOError:
            print('Error: File not saved!')

    def proof_of_work(self):
        last_block = self.__chain[-1]
        lash_block_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, lash_block_hash, proof):
            proof += 1

        return proof

    def get_balance(self, sender=None):

        if sender is not None:
            participant = sender
        else:
            if self.public_key is None:
                return None
            participant = self.public_key

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

    def add_transaction(self, recipient, sender, signature, amount=1.0, broadcast=True):

        if self.public_key is None:
            return False

        transaction = Transactions(
            sender,
            recipient,
            signature,
            amount
        )

        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            if broadcast:
                for node in self.__peer_nodes:

                    url = "http://{}/broadcast-transaction".format(node)
                    try:

                        response = requests.post(url, json={
                            'sender': sender,
                            'recipient': recipient,
                            'amount': amount,
                            'signature': signature
                        })
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined!, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def add_block(self, block):

        transactions = [Transactions(tx['sender'],
                                     tx['recipient'],
                                     tx['signature'],
                                     tx['amount'])
                        for tx in block['transactions']]

        proof_is_valid = Verification.valid_proof(transactions[:-1], block['previous_hash'], block['proof'])
        hashes_match = hash_block(self.get_chain()[-1]) == block['previous_hash']

        if not proof_is_valid or not hashes_match:
            print('proof_is_valid==>>', proof_is_valid)
            print('hashes_match==>>', hashes_match)
            return False

        converted_block = Block(block['index'], block['previous_hash'], transactions, block['proof'],
                                block['timestamp'])
        self.__chain.append(converted_block)

        # remove the local-open transaction if there are in incoming block['transaction']
        stored_open_transactions = self.__open_transactions.copy()
        for open_tx in stored_open_transactions:
            for incoming_tx in block['transactions']:
                if open_tx.sender == incoming_tx['sender'] and open_tx.recipient == incoming_tx['recipient'] and open_tx.signature == incoming_tx['signature']:
                    try:
                        self.__open_transactions.remove(open_tx)
                    except:
                        print('Item was already removed')

        self.save_data()
        return True

    def resolve(self):
        winner_chain = self.__chain
        replace = False
        for node in self.__peer_nodes:
            try:
                url = "http://{}/chain".format(node)
                response = requests.get(url)
                peer_node_chain_raw = response.json()
                peer_node_chain = [
                    Block(block['index'],
                          block['previous_hash'],
                          [
                              Transactions(tx['sender'],
                                           tx['recipient'],
                                           tx['signature'],
                                           tx['amount']
                                           ) for tx in block['transactions']],
                          block['proof'],
                          block['timestamp']
                          ) for block in peer_node_chain_raw]

                peer_node_chain_len = len(peer_node_chain)
                local_node_chain_len = len(winner_chain)

                print('peer_node_chain_len:', peer_node_chain_len)
                print('local_node_chain_len:', local_node_chain_len)

                if peer_node_chain_len > local_node_chain_len and Verification.verify_chain(peer_node_chain):
                    winner_chain = peer_node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue
        self.__chain = winner_chain
        self.resolve_conflicts = False
        if replace:
            self.__open_transactions = []
        self.save_data()
        return replace






    def mine_block(self):

        if self.public_key is None:
            return None, "Mining Failed!, Got no wallet?"

        last_block = self.__chain[-1]

        hashed_block = hash_block(last_block)
        # print("====>>>>>Hashed Block:", hashed_block)

        proof = self.proof_of_work()

        # Mining Reward

        reward_transaction = Transactions(
            MINING,
            self.public_key,
            '',
            MINING_REWARD
        )

        # open_transactions.append(reward_transaction)
        copied_transaction = self.__open_transactions[:]

        # verifying the transactions
        for tx in copied_transaction:
            if not Wallet.verify_transaction(tx):
                return None, "Mining failed!, Transactions are manipulated"

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
        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)

            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined!, needs resolving')
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block, "Mining successful!"

    def add_peer_node(self, node):
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        return list(self.__peer_nodes)[:]
