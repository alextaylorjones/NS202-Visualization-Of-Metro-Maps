from flask import Flask, jsonify, render_template, request
from utils import random_network, convert_networkx
from load_corpus import load_corpus
import networkx as nx
app = Flask(__name__)


@app.route('/_get_intercitation_<int:node_id>')
def get_intercitation(node_id):
    node_id = str(node_id)
    print "ID1:",node_id
    print "Graph has",len(global_graph.nodes()),' nodes'
    if ((node_id) in global_graph):
        print "Global graph has node",node_id
        ancs = nx.ancestors(global_graph,node_id)
        desc = nx.descendants(global_graph,node_id)
        print ancs,desc
        s = nx.DiGraph()
        for a in ancs:
            s.add_node(a)
        for d in desc:
            s.add_node(d)
        return jsonify(convert_networkx(s)['elements'])
    return []





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
    loader = load_corpus('./datasets/','Cit-HepTh.txt','stanford-hepth',600)

    global_graph = loader.get_graph('stanford-hepth')
    app.run(debug=True)
