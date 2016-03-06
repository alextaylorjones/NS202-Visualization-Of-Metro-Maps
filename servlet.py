from flask import Flask, jsonify, render_template, request
from utils import random_network, convert_networkx
app = Flask(__name__)

@app.route("/_get_cy_data")
def random():
    print "called get_cy_data"
    r = random_network()
    c = convert_networkx(r)['elements']

    return jsonify(c)

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()