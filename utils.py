import json
import networkx as nx
from py2cytoscape.util.util_networkx import from_networkx, to_networkx


# Define dictionary of empty network
empty_network = {
        'data': {
            'name': 'awesome visualization'
        },
        'elements': {
            'nodes':[],
            'edges':[]
        }
}

def convert_networkx(nxgraph):
    return from_networkx(nxgraph)

def random_network():
    # g=nx.complete_graph(10)
    g = nx.erdos_renyi_graph(20, 2, 1, directed=True)
    return g

if __name__=="__main__":
    g = random_network()
    print convert_networkx(g)