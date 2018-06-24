from flask import Flask, jsonify, request
from uuid import uuid4
from bc import Blockchain
import json

# instantiate the app
app = Flask(__name__)

# generate a unique address for this node
node_address = str(uuid4()).replace('-','')

# instantiate the blockchain
blockchain = Blockchain()

# basic blockchain functionalities
# - mine a block
# - add new transactions
# - to view the whole blockchain

# API endpoint to mine new blocks
@app.route('/mine', methods=['GET'])
def mine():

	# get the last block of the blockchain
	last_block = blockchain.last_block
	# get the proof of the last block
	last_proof = last_block['proof']

	current_proof = blockchain.proof_of_work(last_proof)

	# Node recieves 1 amount of currency for mining one block
	# sender = 0 means that this amount is send by the blockchain itself
	# This amount=1 is created out of thin air(LOL!)
	blockchain.new_transaction(sender='0', recipient=node_address, amount=1)

	# get the previous hash and add it to the blockchain
	prev_hash = blockchain.hash(last_block)
	block = blockchain.new_block(proof=current_proof, previous_hash=prev_hash)

	response = {
		'message': 'New Block Mined',
		'index': block['index'],
		'transactions': block['transactions'],
		'proof': block['proof'],
		'previous_hash': block['previous_hash']
	}
	return jsonify(response), 200


# API endpoint to add new transactions
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
	value = request.get_json()
	# value['sender'] = request.args.get('sender')
	# value['recipient'] = request.args.get('recipient')
	# value['amount'] = request.args.get('amount')
	# print(value)

	# check for valid data from POST
	if not len(value) == 0:
		required = ['sender', 'recipient', 'amount']
		if not all(k in value for k in required):
			return 'Missing Parameters', 400

		index = blockchain.new_transaction(value['sender'], value['recipient'], value['amount'])
		response = {
			'message': 'Transaction will be added to Block {index}'.format(index=index),
		}

		return jsonify(response), 201

	return 'No Parameters Given', 400

# API endpoint for seeing the whole blockchain
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }

    return jsonify(response), 200

# API endpoint to register the blockchain nodes
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    nodes_list = request.get_json()

    nodes = nodes_list.get('nodes')
    if nodes is None:
        return "Error: Invalid nodes list", 400

    for node in nodes:
        blockchain.register_node(node)
    
    response = {
        'message': 'New nodes has been added to blockchain',
        'total_nodes': list(blockchain.nodes),
    }

    return jsonify(response), 201

# API endpoint to determine consensus
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    isconflict = blockchain.maintain_consensus()

    if isconflict:
        response = {
            'message': 'Our chain was replaced by the valid chain',
            'new_chain': blockchain.chain,
        }
    else:
        response = {
            'message': 'Our chain is valid',
            'chain': blockchain.chain,
        }
    
    return jsonify(response), 201


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to connect')
    args = parser.parse_args()
    port = args.port
    
    app.run(port=port, debug=True)