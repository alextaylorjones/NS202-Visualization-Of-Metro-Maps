from flask import Flask, jsonify, render_template, request
from utils import random_network, convert_networkx
from load_corpus import load_corpus
import networkx as nx
import random
import math
app = Flask(__name__)

SAMPLES_TO_LOAD = 7000


def num_edges_to_remove():
    return math.floor(max(0, SAMPLES_TO_LOAD - 500) * .6)

def num_nodes_to_remove():

    return math.floor(max(0, SAMPLES_TO_LOAD - 500) * .2)


def get_global_graph():
    # Load a corpus into memory
    loader = load_corpus('./datasets/', 'Cit-HepTh.txt', 'stanford-hepth', SAMPLES_TO_LOAD)
    g = loader.get_graph('stanford-hepth')

    return g

def sparsify_graph(g):
    print "sparsifying"
    edges = g.edges()
    remove = random.sample(edges, int(num_edges_to_remove()))
    g.remove_edges_from(remove)

    nodes = g.nodes()
    rm = random.sample(nodes, int(num_nodes_to_remove()))
    g.remove_nodes_from(rm)
    return g


def assign_relative_positions(graph):
    '''
    Assign the relative position of the graph on viewport
    need to take into account number of descendants for beautification
    :param graph:
    :return:
    '''
    print "assigning relative col/rows to graph"
    years = list(set([attrdict["year"] for n,attrdict in graph.node.items()]))
    print years
    yearGraphDict = {}
    for year in years:
        yearGraphDict[year] = [n for n,attrdict in graph.node.items() if attrdict["year"] == year]

    i = 0
    for k in sorted(yearGraphDict.keys()):
        papers = yearGraphDict[k]
        j = -len(papers)/2.
        for n in papers:
            mos_scale = float(graph.node[n]['date'])/12. - .5


            graph.node[n]['row'] = i + mos_scale
            graph.node[n]['col'] = j
            j += 1
        i += 1

    print graph
    nx.info(graph)
    return graph


@app.route('/_get_intercitation_<int:node_id>')
def get_intercitation(node_id):

    graph = get_global_graph()

    node_id = str(node_id)
    # print "ID1:", node_id
    # print "Graph has", len(global_graph.nodes()), ' nodes'
    if ((node_id) in graph):
        print "Global graph has node", node_id
        related = []
        related.extend(nx.ancestors(graph, node_id))
        related.extend(nx.descendants(graph, node_id))
        related.extend([node_id])

        print related

        s = nx.DiGraph(graph.subgraph(related).copy())

        # print "returning subgraph"
        # nx.info(s)
        # print s.nodes()
        # print s.edges()

        g = assign_relative_positions(s)

        nx.info(s)
        return jsonify(convert_networkx(g)['elements'])
    return []


@app.route("/_get_cy_data")
def get_full_graph():
    print "called get_cy_data"
    graph = get_global_graph()
    sparsify_graph(graph)
    g = assign_relative_positions(graph)
    c = convert_networkx(g)['elements']

    return jsonify(c)


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
