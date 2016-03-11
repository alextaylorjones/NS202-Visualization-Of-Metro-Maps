from flask import Flask, jsonify, render_template, request
from utils import random_network, convert_networkx
from load_corpus import load_corpus
import networkx as nx
import random
import math
from tree_intersection import TreeIntersection
app = Flask(__name__)

SAMPLES_TO_LOAD = 5000

def num_edges_to_remove(size):
    return math.floor(max(0,  size - 300) * .7)

def num_nodes_to_remove(size):
    return math.floor(max(0, size - 300) * .5)


def get_global_graph():
    # Load a corpus into memory
    loader = load_corpus('./datasets/', 'Cit-HepTh.txt', 'stanford-hepth', SAMPLES_TO_LOAD)
    g = loader.get_graph('stanford-hepth')

    return g

def sparsify_graph(g):
    print "sparsifying"
    edges = g.edges()
    print "removing edges: " + str(num_edges_to_remove(len(edges)))
    remove = random.sample(edges, int(num_edges_to_remove(len(edges))))
    g.remove_edges_from(remove)

    nodes = g.nodes()
    rm = random.sample(nodes, int(num_nodes_to_remove(len(nodes))))
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


@app.route('/_get_intercitation/<src>/<dst>')
def get_intercitation(src, dst):

    graph = get_global_graph()

    nodes = [graph.node[src], graph.node[dst]]
    nodes = sorted(nodes, key=lambda n: (n['year'], n['date']))

    print 'getting nodes...'
    print nodes

    t = TreeIntersection()

    dag = t.get_intercitation_dag(nodes[1]['file_id'], nodes[0]['file_id'], graph)
#    dag = t.add_relevant_citing_nodes(dag, graph, .25)

    # dag = t.add_cited_citing_nodes(dag, graph)

    s = nx.DiGraph(graph.subgraph(dag.nodes()).copy())
    g = assign_relative_positions(s)

    return jsonify(convert_networkx(g)['elements'])


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
