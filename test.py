import networkx as nx
from load_corpus import load_corpus
from influence_graph import influence_graph
#Load a corpus into memory
loader = load_corpus('/home/alex/classes/NS202/project/NS202-METRO-MAP-VISUALIZATION-OF-CITATION-NETWORKS/datasets/','Cit-HepTh.txt','stanford-hepth',500)
#Get the loaded graph
graph = loader.get_graph('stanford-hepth')

#Create the influence graphs based 
#hardcoded concepts for now
concepts = ['we']
influence = influence_graph(graph, concepts)
influence.construct_influence_graph(loader.get_author_dict())
influence.compute_document_pair_influences(0.1)

igraph = influence.get_influence_graph()

#Visualize the ancestral relation of the most related papers
max_edge = None
max_edge_weight = -100
for e in igraph.edges():
    temp_weight = 0
    for key in igraph.edge[e[0]][e[1]]['weight']:
        temp_weight += igraph.edge[e[0]][e[1]]['weight'][key]
    if temp_weight > max_edge_weight:
        max_edge = e
        max_edge_weight = temp_weight

#Visualize path between nodes in max_edge

