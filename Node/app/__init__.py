from flask import Flask
from app.blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()


from app import routes