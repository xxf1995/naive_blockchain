'''
server of the naive_blockchain
Created by Xingfan Xia
@12:24 AM 01-21-2018
'''
import requests

from flask import Flask, jsonify, request
from flask_cors import CORS
from textwrap import dedent
from uuid import uuid4

from blockchain import Blockchain

app = Flask(__name__)
CORS(app)
# global unique address for node with Universally Unique Identifiers as described in RFC 4122.
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route("/", methods=['GET'])
def hello():
	return jsonify("Welcome to Naive Blockchain!")

@app.route('/mine', methods=['Get'])
def mine():
	# Gen proof with proof of work algo
	last_block = blockchain.last_block
	last_proof = last_block['proof']
	proof = blockchain.proof_of_work(last_proof)

	# Reward for mining, sender set to '0' to indicate it's issued by
	# the system & this node has mined a new coin
	blockchain.new_transaction(
		sender=blockchain.sys_issuer,
		recipient=node_identifier,
		amount=1
	)

	# Forge this new block by adding to chain
	previous_hash = blockchain.hash_block(last_block)
	block = blockchain.new_block(proof, previous_hash)

	response = {
		'message': "New Block Mined and Forged",
		'index': block['index'],
		'transactions': block['transactions'],
		'proof': block['proof'],
		'previous_hash': block['previous_hash']
	}
	return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
	payload = request.get_json()
	print(payload)
	required = ['sender', 'recipient', 'amount']
	if not all(key in payload for key in required):
		return "Invalid transaction data posted", 400

	index = blockchain.new_transaction(payload['sender'],
	                                   payload['recipient'],
	                                   payload['amount'])

	if index == -999:
		response = {'message': f"Transaction Denied", "Error": "Sender does not have enough balance to make this transaction" }
	else:
		response = {'message': f"Transaction successfully added at Block {index}"}

	return jsonify(response), 201


@app.route('/chain', methods=['Get'])
def full_chain():
	response = {
		'chain': blockchain.chain,
		'length': len(blockchain.chain)
	}

	return jsonify(response), 200

@app.route('/balance', methods=['Get'])
def get_balance():
	address = request.args.get('addr')
	balance = blockchain.wallet_balance(address)
	response = {'message': f"Your balance is {balance}"}

	return jsonify(response), 201

@app.route('/save')
def save_chain():
	blockchain.save_chain()

	response = {'message': "Successfully saved"}
	return jsonify(response), 201

@app.route('/load')
def load_chain():
	blockchain.load_chain()
	response = {'message': "Successfully loaded"}
	return jsonify(response), 201

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=2333, debug=True)
