from flask import Flask, jsonify, render_template, request
from utils import random_network, convert_networkx
from load_corpus import load_corpus
app = Flask(__name__)

@app.route('/_get_intercitation_<int:id1>_<int:id2>')
def get_intercitation(id1,id2):
    print "ID1:",id1
    print "ID2:",id2



@app.route("/_get_cy_data")
def random():
    print "called get_cy_data"
    c = convert_networkx(global_graph)['elements']

    return jsonify(c)

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    global_graph = None
 
    #Load a corpus into memory
    loader = load_corpus('./datasets/','Cit-HepTh.txt','stanford-hepth',100)

    global_graph = loader.get_graph('stanford-hepth')
    app.run(debug=True)
