from flask import Flask
from data_loader import load_all


app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'