from flask import Flask, jsonify, render_template, request
from utils import random_network, convert_networkx
from influence_graph import influence_graph
from load_corpus import load_corpus
from concept_helper import concept_helper
from coherence_graph import coherence_graph
import networkx as nx
import random
import math
from tree_intersection import TreeIntersection

app = Flask(__name__)

SAMPLES_TO_LOAD = 5000
NODE_COUNT_SCALER = 50

def num_edges_to_remove(size):
    return math.floor(max(0, size - 100) * .95)


def num_nodes_to_remove(size):
    return math.floor(max(0, size - 300) * .2)


def get_global_graph(num_samples=SAMPLES_TO_LOAD):
    # Load a corpus into memory

    g = global_graph.copy()
    nodes = g.nodes()
    random.seed(1)
    samples = random.sample(nodes, int(min(num_samples, len(nodes))))
    subgraph = nx.DiGraph(g.subgraph(samples));

    return subgraph

def sparsify_graph(g):

    print "sparsifying"

    random.seed(1)

    nodes = g.nodes()
    rm = random.sample(nodes, int(num_nodes_to_remove(len(nodes))))
    g.remove_nodes_from(rm)

    edges = g.edges()
    # print "removing edges: " + str(num_edges_to_remove(len(edges)))
    remove = random.sample(edges, int(num_edges_to_remove(len(edges))))
    g.remove_edges_from(remove)

    return g


def assign_relative_positions(graph):
    '''
    Assign the relative position of the graph on viewport
    need to take into account number of descendants for beautification
    :param graph:
    :return:
    '''
    print "assigning relative col/rows to graph"
    years = list(set([attrdict["year"] for n, attrdict in graph.node.items()]))
    # print years
    yearGraphDict = {}
    for year in years:
        yearGraphDict[year] = [n for n, attrdict in graph.node.items() if attrdict["year"] == year]

    i = 0
    row_scaler = max(1, max([len(p) for p in yearGraphDict.values()]) / NODE_COUNT_SCALER)
    for k in sorted(yearGraphDict.keys()):
        papers = yearGraphDict[k]
        j = -len(papers) / 2.

        for n in papers:
            mos_scale = float(graph.node[n]['date']) / 12. - .4

            graph.node[n]['row'] = i + mos_scale
            graph.node[n]['col'] = j
            j += 1
        i += row_scaler

    # print graph
    # nx.info(graph)
    return graph


@app.route('/_get_intercitation/<src>/<dst>/<algo>')
def get_intercitation(src, dst, algo):
    graph = get_global_graph()

    nodes = [graph.node[src], graph.node[dst]]
    nodes = sorted(nodes, key=lambda n: (n['year'], n['date']))

    print 'getting nodes...'
    # print nodes

    t = TreeIntersection()

    print "getting intercitation dag"
    dag = t.get_intercitation_dag(nodes[1]['file_id'], nodes[0]['file_id'], graph)
    print "getting relevant citing nodes"
    #citing param adds that many percentage of most related nodes in entire graph
    #through common citations
    citing_relevance_parameter = 0.20
    #SWITCH HERE BASED ON USER PARAMS
    #do nothing if selected full intercitation
    if algo == "netrel":
        print "getting netrel"
        dag = t.add_relevant_citing_nodes(dag, graph, citing_relevance_parameter)
    elif algo == "bushy":
        print "getting bushy"
        dag = t.add_cited_citing_nodes(dag, graph)

    num_concepts = int(2*math.log(len(list(dag.nodes()))))
    print "extracting concepts"
    concepts = concept_help.extract(dag,nodes[1]['abstract'], nodes[0]['abstract'],num_concepts)
    print "Extracted concepts:",concepts
    influence_helper.reset_concepts(concepts)
    print "Constructing influence_helper.graph"
    influence_helper.construct_influence_graph(loader.get_author_dict())
    # print "Sample to compute influence_helper. for concepts"
    influence_helper.compute_document_pair_influences(0.2)#0.05 error prob
    igraph = influence_helper.get_influence_graph()

    print "Creating coherence graph"
    num_chains = 25*len(list(dag.nodes()))
    min_length_chains = 2
    min_coherence = 0.001
    print "Initializing cohrence graph"
    cohG = coherence_graph(igraph,concepts,num_chains,min_length_chains,min_coherence)
    print "Greedily creating coherence graph"
    cohG.greedy_coherence_graph_create(dag)

    num_samples = 1000
    related_param = 0.2
    print "Sampling coherent paths"
    cohG.randomly_sample_coherent_paths(nodes[1]['file_id'], num_samples,related_param)

    print "Ranking intercitation tree based on coverage"
    dag = cohG.rank_dag_according_to_coverage(dag)
    #
    # for d in dag.nodes():
    #     print dag.node[d]['coverage']

    s = nx.DiGraph(graph.subgraph(dag.nodes()).copy())
    for d in dag.nodes():
        s.node[d]['coverage'] = 1. - dag.node[d]['coverage']/float(len(dag.nodes()))

    g = assign_relative_positions(s)

    return jsonify(convert_networkx(g)['elements'])


@app.route("/_get_cy_data/<size>")
def get_full_graph(size):
    print "generating graph of size: " + str(size)
    graph = get_global_graph(num_samples=int(size))
    sparsify_graph(graph)
    g = assign_relative_positions(graph)
    c = convert_networkx(g)['elements']

    return jsonify(c)


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == "__main__":
    print "Loading global graph"
    loader = load_corpus('./datasets/', 'Cit-HepTh.txt', 'stanford-hepth', SAMPLES_TO_LOAD)
    global_graph = loader.get_graph('stanford-hepth')
    init_concepts = []
    print "Initializing influence graph helper"
    influence_helper = influence_graph(global_graph, init_concepts)
    print "Initializing concept helper"
    concept_help = concept_helper(global_graph)

    app.run(host="0.0.0.0", debug=True)
