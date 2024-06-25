from flask import Flask, jsonify, request
from flask_cors import CORS
from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)

CORS(app)

@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():

        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving the keys failed!'
        }
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():

        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading the keys failed!'
        }
        return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()

    if balance is not None:
        response = {
            'message': 'Balance fetched successfully!',
            'public_key': wallet.public_key,
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading balance failed!',
            'wallet_setup': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/', methods=['GET'])
def get_ui():
    return 'This works!'


@app.route('/transaction', methods=['POST'])
def add_transaction():

    if wallet.public_key is None:
        response = {
            'message': 'No wallet set up'
        }
        return jsonify(response), 400

    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found!'
        }
        return jsonify(response), 400

    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required Data is missing',
        }
        return jsonify(response), 400

    recipient = values['recipient']
    amount = values['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    is_success = blockchain.add_transaction(recipient, wallet.public_key, signature, amount)
    if is_success:
        response = {
            'message': 'Transaction created successfully!',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }

        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating the transaction failed!'
        }
        return jsonify(response), 500

@app.route('/mine', methods=['POST'])
def mine():

    block, msg = blockchain.mine_block()
    if block is not None:
        hashed_block = block.__dict__.copy()
        hashed_block['transactions'] = [tx.__dict__ for tx in hashed_block['transactions']]
        response = {
            'message': msg,
            'block': hashed_block,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 200
    else:
        response = {
            'message': msg,
            'wallet_setup': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/chain', methods=['GET', 'POST'])
def get_chain():
    chain_snapshot = blockchain.get_chain()

    dict_chain = [block.__dict__.copy() for block in chain_snapshot]

    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain), 200


@app.route('/transactions', methods=['GET'])
def get_open_transactions():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    response = {
        'message': 'Transactions fetched successfully!',
        'transactions': dict_transactions
    }
    return jsonify(response), 200




if __name__ == '__main__':
    app.run('0.0.0.0', port=3000)
