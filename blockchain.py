import json
from collections import OrderedDict
from hash_util import hash_string, hash_block
import pickle

# Init the blockchain list


MINING_REWARD = 10



MINING = 'MINING'

# sender = 'sender'
# recipient = 'recipient'
# amount = 'amount'

blockchain = []
open_transactions = []
owner = 'Mukul'

participants = {'Mukul'}


def load_data():

    global blockchain
    global open_transactions

    try:
        with open('blockchain.txt', mode='r') as f:
            file_content = f.readlines()
            blockchain = json.loads(file_content[0][:-1])
            updated_blockchain = []
            for block in blockchain:
                updated_block = {
                    'previous_hash': block['previous_hash'],
                    'index': block['index'],
                    'proof': block['proof'],
                    'transactions': [OrderedDict([
                        ('sender', tx['sender']),
                        ('recipient', tx['recipient']),
                        ('amount', tx['amount'])
                    ]) for tx in block['transactions']]
                }
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain
            open_transactions = json.loads(file_content[1])

            updated_open_transactions = []
            for open_tx in open_transactions:
                updated_open_tx = OrderedDict([
                    ('sender', open_tx['sender']),
                    ('recipient', open_tx['recipient']),
                    ('amount', open_tx['amount'])
                ])
                updated_open_transactions.append(updated_open_tx)
            open_transactions = updated_open_transactions
    except IOError:
        print('File not found!')

        # Starting block of the blockchain
        genesis_block = {
            'previous_hash': '',
            'index': 0,
            'transactions': [],
            'proof': 100
        }
        blockchain = blockchain[genesis_block]
        open_transactions = []

        # Pickle module
        # with open('blockchain.p', mode='rb') as f:
        #     file_content = pickle.loads(f.read())
        #
        #     global blockchain
        #     global open_transactions
        #
        #     blockchain = file_content['chain']
        #     open_transactions = file_content['ot']
    finally:
        print('Cleanup!')


load_data()


def save_data():
    try:
        with open('blockchain.txt', mode='w') as f:
            f.write(json.dumps(blockchain))
            f.write('\n')
            f.write(json.dumps(open_transactions))

        # with open('blockchain.p', mode='wb') as f:
        #     save_data_payload = {
        #         'chain': blockchain,
        #         'ot': open_transactions
        #     }
        #     f.write(pickle.dumps(save_data_payload))
    except IOError:
        print('Error: File not saved!')



def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof))
    print("guess: ", guess)
    guess_hash = hash_string(guess)
    print("guess_hash: ", guess_hash)
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    lash_block_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, lash_block_hash, proof):
        proof += 1

    return proof


def get_balance(participant):
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    open_transaction_sender_amount = [open_tx['amount'] for open_tx in open_transactions if
                                      open_tx['sender'] == participant]
    tx_sender.append(open_transaction_sender_amount)

    tx_send_amount = 0
    for tx in tx_sender:
        for amount_sent in tx:
            tx_send_amount += amount_sent

    tx_receiver = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in
                   blockchain]
    tx_receive_amount = 0
    for tx in tx_receiver:
        for amount_received in tx:
            tx_receive_amount += amount_received

    return tx_receive_amount - tx_send_amount


def get_last_blockchain_value():
    """ Returns the last value of current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    sender_amount = get_balance(transaction['sender'])
    return sender_amount >= transaction['amount']


def add_transaction(recipient, sender=owner, amount=1.0):
    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    # }

    transaction = OrderedDict([
        ('sender', sender),
        ('recipient', recipient),
        ('amount', amount)
    ])

    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True

    return False


def mine_block():
    last_block = blockchain[-1]

    hashed_block = hash_block(last_block)
    print("====>>>>>Hashed Block:", hashed_block)

    proof = proof_of_work()

    # Mining Reward
    reward_transaction = OrderedDict([
        ('sender', MINING),
        ('recipient', owner),
        ('amount', MINING_REWARD)
    ])

    # open_transactions.append(reward_transaction)
    copied_transaction = open_transactions[:]
    copied_transaction.append(reward_transaction)

    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transaction,
        'proof': proof
    }
    blockchain.append(block)
    return True


def get_transaction_value():
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input('Your transaction amount please: '))

    return tx_recipient, tx_amount


def get_user_choice():
    return input('Your choice: ')


def print_blockchain_elements():
    # Output the blockchain list to the console
    for block in blockchain:
        print('Outputting block')
        print(block)
    else:
        print('-' * 20)


def verify_chain():
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('Proof of work is invalid')
            return False

    return True


def verify_transactions():
    return all(verify_transaction(tx) for tx in open_transactions)


waiting_for_input = True

while waiting_for_input:
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain block')
    print('4: Output the Participants')
    print('5: Check transactions validity')
    print('h: Manipulate the chain')
    # print('v: Verify the chain')
    print('q: Quit')

    user_choice = get_user_choice()

    print('-' * 10, 'Choice Registered', '-' * 10)

    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        if add_transaction(recipient, amount=amount):
            print('Transaction added.')
        else:
            print('Invalid transaction')
        print(open_transactions)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid.')
        else:
            print('There are invalid transactions')
    elif user_choice == 'h':
        blockchain[0] = {
            'previous_hash': '',
            'index': 0,
            'transactions': [{'sender': 'Chris', 'recipient': 'Max', 'amount': 33}]
        }
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please check the value from the list!')

    if not verify_chain():
        print('Blockchain is invalid!')
        print_blockchain_elements()
        break
    print('Balance of {}: {:6.2f}'.format(owner, get_balance(owner)))
    # print("get_balance-->>", get_balance(owner))
else:
    print('User Left!')

print('Done!')
