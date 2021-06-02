import json
import hashlib
from time import time
from urllib.parse import urlparse
import requests

class BlockChain():
    def __init__(self):
        self.nodes = set()
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash=1,proof=100)

    def new_block(self,proof,previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transaction': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        self.current_transactions = []
        self.chain.append(block)
        return block


    def new_transaction(self,sender,recipient,amount):
        self.current_transactions.append(
            {
                'sender':sender,
                'recipient': recipient,
                'amount':amount,
            }
        )
        return self.last_block['index'] + 1
        

    def proof_of_work(self,last_proof):
        proof = 0

        while self.valid_proof(last_proof,proof) is False:
            proof = proof  + 1

        return proof

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)


    def valid_chain(self,chain):

        last = chain[0]
        ci = 1
        while ci < len(chain):
            block = chain[ci]
            print(f'{last}')
            print(f'{block}')
            print("\n-----------------------\n")

            if block['previous_hash'] != self.hash(last):
                return False

            last = block
            ci = ci + 1
        return True 


    def resolve_conflicts(self):
        neighbour = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbour:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False



    @staticmethod
    def valid_proof(last_proof,proof):
        g = f'{last_proof}{proof}'.encode()
        g_hash= hashlib.sha256(g).hexdigest()
        return g_hash[:4] == "0000"



    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]