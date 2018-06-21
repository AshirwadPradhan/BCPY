import hashlib
import json
from time import time
from uuid import uuid4

class Blockchain(object):
	def __init__(self):
		self.chain = []
		self.current_transactions = []

		# creation of genesis block
		self.new_block(proof=100, previous_hash=1)

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
