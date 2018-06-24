import hashlib
import json
from time import time
from uuid import uuid4
from urllib.parse import urlparse
import requests

class Blockchain(object):
	def __init__(self):
		self.chain = []
		self.current_transactions = []
		# collection of nodes connected to the blockchain
		self.nodes = set()

		# creation of genesis block
		self.new_block(proof=100, previous_hash=1)

	def register_node(self, address):
		'''
		Register a new node in the blockchain
		
		:param address: <str> IP address of the node
		:return: None
		'''

		node_address = urlparse(address)
		self.nodes.add(node_address.netloc)


	def new_block(self, proof, previous_hash=None):
		"""
		Creates a new block and add it to the chain

		:param proof: <int> proof given by the proof of work algrithm
		:param previous_hash: <str> hash of the previous work
		:return: <dict> new block
		"""

		# declaration of new block
		block = {
			'index': len(self.chain) + 1,
			'timestamp': time(),
			'transactions': self.current_transactions,
			'proof': proof,
			'previous_hash': previous_hash or self.hash(self.chain[-1]),
		}

		# make number of transactions in the current block to be empty
		self.current_transactions = []

		# append the new block to the blockchain
		self.chain.append(block)

		# return the new block which is created
		return block

	def new_transaction(self, sender, recipient, amount):
		"""
		Creates a new transaction and add it to the lists of transaction

		:param sender: <str> Address of the sender
		:param recipient: <str> Address of the recipient
		:param amount: <int> Amount
		:return: <int> index of the block in which the transaction is added
		"""
		self.current_transactions.append({
			'sender': sender,
			'recipient': recipient,
			'amount': amount,
			})

		return self.last_block['index'] + 1

	@staticmethod
	def hash(block):
		"""
		Creates a SHA-256 hash of a block

		:param block: <dict> block
		:return: <str>
		"""

		# we must maintain an ordered dictionary so that we get same hash for the same block everytime
		# as python dictionaries are undorderd by default so we use sort_keys param 
		block_string = json.dumps(block, sort_keys=True).encode()

		return hashlib.sha256(block_string).hexdigest()

	@property
	def last_block(self):
		# returns the last block in the chain
		return self.chain[-1]
	
	@staticmethod
	def valid_proof(last_proof, proof):
		"""
		Computes h(last_proof, proof) contains 4 leading zeros

		:param last_proof: <int> last proof
		:param proof: <int> new proof to check
		:return: <bool> returns wether this proof is valid or not
		"""

		guess = '{last_proof}{proof}'.format(last_proof=last_proof, proof=proof).encode()
		guess_hash = hashlib.sha256(guess).hexdigest()

		# the number of zeros gives us the difficulty of the algorithm
		# we can manipulate the number of zeros to increase or decrease the difficulty
		return guess_hash[:4] == '0000'
	
	def proof_of_work(self, last_proof):
		"""
		PoW algorithm for the blockchain
		-Find a number p' such that hash(pp') contains 4 leading zeros
		-p is the previous proof and p' is the new proof

		:param last_proof: <int> previous proof
		:return: <int> new proof
		"""
		proof = 0
		while self.valid_proof(last_proof, proof) is False:
			proof += 1

		return proof
	
	def valid_chain(self, chain):
		"""
		Verifies if the blockchain is valid or not

		:param chain: <list> blockchain to verify
		:return: <bool> True if blockchain is valid and False if not
		"""
		last_block = chain[0]
		current_index = 1

		# check for each block and verify if hash and proof of work is correct
		while current_index < len(chain):
			current_block = chain[current_index]
			print('{}'.format(last_block))
			print('{}'.format(current_block))
			print('\n'+'-'*20+'\n')

			# check if the hash of the block is correct
			if current_block['previous_hash'] != self.hash(last_block):
				return False
			
			# check if the Proof of work is correct
			if not self.valid_proof(last_block['proof'], current_block['proof']):
				return False
			
			last_block = current_block
			current_index += 1
	
		return True
	
	def maintain_consensus(self):
		"""
		This is consensus algorithm. 
		It resolves the conflicts by replacing our chain with the longest chain in the network

		:return: <bool> True if our chain is replaced. False if not
		"""
		peers = self.nodes
		new_chain = None

		# initialize maximum length as the length of the current node chain
		max_len = len(self.chain)

		# get the chain information from every node in the network
		for node in peers:
			# get the chain
			response = requests.get('http://{}/chain'.format(node))

			# check if the node is alive
			if response.status_code == '200':
				# get the chain length and the chain
				response_length = response.json()['length']
				response_chain = response.json()['chain']

				# check if the chain from other node is valid and longer than this node chain
				if response_length > max_len and self.valid_chain(response_chain):
					max_len = response_length
					new_chain = response_chain
		
		# if new chain has been found replace this chain with new found chain
		if new_chain:
			self.chain = new_chain
			return True
		
		return False
