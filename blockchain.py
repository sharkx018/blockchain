import json
from hash_util import hash_block
from oop.block import Block
from oop.transactions import Transactions
from oop.verfication import Verification

# Init the blockchain list
blockchain = []
owner = 'Mukul'
participants = {'Mukul'}

# Mining Config
MINING_REWARD = 10
MINING = 'MINING'

open_transactions = []


def load_data():
    global blockchain
    global open_transactions

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
            blockchain = updated_blockchain
            open_transactions = json.loads(file_content[1])

            updated_open_transactions = []
            for open_tx in open_transactions:
                updated_open_tx = Transactions(
                    open_tx['sender'],
                    open_tx['recipient'],
                    open_tx['amount']
                )
                updated_open_transactions.append(updated_open_tx)
            open_transactions = updated_open_transactions
    except:
        print('File not found!')

        # Starting block of the blockchain
        genesis_block = Block(0, '', [], 100, 0)
        blockchain = [genesis_block]
        open_transactions = []
    finally:
        print('Cleanup!')


load_data()


def save_data():
    try:
        with open('blockchain.txt', mode='w') as f:

            savable_chain = [block.__dict__.copy() for block in [
                Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions],
                      block_el.proof, block_el.timestamp) for block_el in blockchain]]

            f.write(json.dumps(savable_chain))
            f.write('\n')
            savable_transactions = [open_tx.__dict__.copy() for open_tx in open_transactions]
            f.write(json.dumps(savable_transactions))


    except IOError:
        print('Error: File not saved!')


def proof_of_work():
    last_block = blockchain[-1]
    lash_block_hash = hash_block(last_block)
    proof = 0
    verifier = Verification()
    while not verifier.valid_proof(open_transactions, lash_block_hash, proof):
        proof += 1

    return proof


def get_balance(participant):
    tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in blockchain]
    open_transaction_sender_amount = [open_tx.amount for open_tx in open_transactions if
                                      open_tx.sender == participant]
    tx_sender.append(open_transaction_sender_amount)

    tx_send_amount = 0
    for tx in tx_sender:
        for amount_sent in tx:
            tx_send_amount += amount_sent

    tx_receiver = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in
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


def add_transaction(recipient, sender=owner, amount=1.0):
    transaction = Transactions(
        sender,
        recipient,
        amount
    )

    verifier = Verification()

    if verifier.verify_transaction(transaction, get_balance):
        open_transactions.append(transaction)
        save_data()
        return True

    return False


def mine_block():
    last_block = blockchain[-1]

    hashed_block = hash_block(last_block)
    print("====>>>>>Hashed Block:", hashed_block)

    proof = proof_of_work()

    # Mining Reward

    reward_transaction = Transactions(
        MINING,
        owner,
        MINING_REWARD
    )

    # open_transactions.append(reward_transaction)
    copied_transaction = open_transactions[:]
    copied_transaction.append(reward_transaction)

    block = Block(
        len(blockchain),
        hashed_block,
        copied_transaction,
        proof,
    )

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


waiting_for_input = True

while waiting_for_input:
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain block')
    print('5: Check transactions validity')
    # print('v: Verify the chain')
    print('q: Quit')

    user_choice = get_user_choice()

    print('-' * 10, 'Choice Registered', '-' * 10)

    verifier = Verification()

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
    elif user_choice == '5':

        if verifier.verify_transactions(open_transactions, get_balance):
            print('All transactions are valid.')
        else:
            print('There are invalid transactions')
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please check the value from the list!')

    if not verifier.verify_chain(blockchain):
        print_blockchain_elements()
        break
    print('Balance of {}: {:6.2f}'.format(owner, get_balance(owner)))
    # print("get_balance-->>", get_balance(owner))
else:
    print('User Left!')

print('Done!')
