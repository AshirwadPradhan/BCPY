from flask import Flask
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
@app.route('/mine', methods=['GET'])
def mine():
    return 'We will mine a new block'

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    return 'We will add new transactions'

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)