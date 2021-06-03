import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify , request

from trishoolcoin import BlockChain

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')
blockchain = BlockChain()


@app.route('/mine', methods=['GET'])
def mine():
    l_block = blockchain.last_block
    l_proof = l_block['proof']
    proof = blockchain.proof_of_work(l_proof)
    blockchain.new_transaction(sender="0",recipient=node_identifier,amount=1)
    prev_hash = blockchain.hash(l_block)
    block = blockchain.new_block(proof,prev_hash)

    response = {
        'message': "NEW BLOCK MINED",
        'index': block['index'],
        'transactions': block['transaction'],
        'proof': block['proof'],
        'prev_hash': block['previous_hash']
    }

    return jsonify(response), 200






@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    req = ['sender','recipient','amount']
    if not all(k in values for k in req):
        return 'missing values', 400

    index = blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])    
    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201



@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replace = blockchain.resolve_conflicts()
    if replace:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200






if __name__ == '__main__':

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
