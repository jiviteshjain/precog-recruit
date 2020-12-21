from flask import Flask, render_template
from data_loader import get_all


app = Flask(__name__)

@app.route('/')
def index():
    data = get_all()
    return render_template('index.html', data=data)