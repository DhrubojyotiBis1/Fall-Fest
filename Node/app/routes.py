from app import app, blockchain
from  flask import request
import requests
import socket

#BLOCKCHAIN API
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    node = request.args.get('node')
    if node is None:
        return 'No node', 400
    blockchain.add_node(node)   
    return node, 201

@app.route('/connect', methods=['GET'])
def connect():
    response_code = 400
    nodes = []
    existing_node_json = request.get_json()
    if existing_node_json:
        existing_node = existing_node_json.get('ex_node')
        self_node_port = existing_node_json.get('self_port')
        self_node = f'{request.remote_addr}:{self_node_port}'
        if existing_node and existing_node != self_node:
            url = f'http://{existing_node}/nodes'
            response = requests.get(url)
            existing_nodes = response.json()['nodes']
            existing_nodes.append(existing_node)
            for node in existing_nodes:
                if node != self_node:
                    node = 'http://' + node
                    url = f'{node}/connect_node?node=http://{self_node}'
                    response = requests.post(url)
                    if response.status_code == 201:
                        blockchain.add_node(node)
                        nodes.append(node)
            if len(blockchain.nodes):
                #could update the chain here 
                response_code = 201
    return {'nodes': nodes}, response_code


@app.route('/nodes', methods = ['GET'])
def nodes():
    serialised_nodes = []
    for node in blockchain.nodes:
        serialised_nodes.append(node)
    return {'nodes': serialised_nodes}, 200



@app.route('/add_transaction', methods=['POST'])
def add_transactions():
    if not blockchain.hospital_name:
        blockchain.hospital_name = request.remote_addr

    didAdd = False
    response_code = 400
    json = request.get_json()
    transaction = json.get('transaction')
    
    if transaction is None:
       return 'No transaction', response_code

    blockchain.make_transaction(transaction)

    #adding block to blockchain
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.create_block(proof, previous_hash)

    return 'Block hasbeen added', 200


@app.route('/chain', methods = ['GET'])
def chain():
    blockchain.update_chain()
    return get_current_chain(), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    return get_current_chain()

def get_current_chain():
    return {'chain': blockchain.chain, 'length': len(blockchain.chain)}