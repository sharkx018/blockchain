from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('ui', 'node.html')


@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()

    global blockchain
    is_save = True

    if not is_save:
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201

    if is_save and wallet.save_keys():
        blockchain = Blockchain(wallet.public_key, port)
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
        blockchain = Blockchain(wallet.public_key, port)
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


@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {
            'message': "No Data found",
        }
        return jsonify(response), 400

    required_fields = ['sender', 'recipient', 'amount', 'signature']
    if not all(req_field in values for req_field in required_fields):
        response = {
            'message': 'Required Data is missing'
        }
        return jsonify(response), 400
    is_success = blockchain.add_transaction(values['recipient'], values['sender'], values['signature'], values['amount'], False)
    if is_success:
        response = {
            'message': 'Transaction created successfully!',
            'transaction': {
                'sender': values['sender'],
                'recipient': values['recipient'],
                'amount': values['amount'],
                'signature': values['signature']
            }
        }

        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating the transaction failed!'
        }
        return jsonify(response), 500

@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found'
        }
        return jsonify(response), 400

    if 'block' not in values:
        response = {'Block data is missing'}
        return jsonify(response), 400

    block = values['block']

    if block['index'] == blockchain.get_chain()[-1].index + 1:
        if blockchain.add_block(block):
            response = {
                'message': 'Block added'
            }
            return jsonify(response), 201
        else:
            response = {
                'message': 'Block seems invalid.'
            }
            return jsonify(response), 500
    elif block['index'] > blockchain.get_chain()[-1].index:
        pass
    else:
        response = {'message': 'Blockchain seems to be shorter, block not added'}
        jsonify(response), 409








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
    # response = {
    #     'message': 'Transactions fetched successfully!',
    #     'transactions': dict_transactions
    # }
    return jsonify(dict_transactions), 200


@app.route('/node', methods=['POST'])
def add_route():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached'
        }
        return jsonify(response), 400

    if 'node' not in values:
        response = {
            'message': 'No Node data found'
        }
        return jsonify(response), 400

    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added successfully',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url is None or node_url is '':
        response = {
            'message': 'No node found'
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'Node removed!',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    response = {
        'message': 'All nodes fetched successfully',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=3000)
    args = parser.parse_args()
    print(args)
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run('0.0.0.0', port=port)
