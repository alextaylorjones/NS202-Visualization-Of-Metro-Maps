import networkx as nx
from load_corpus import load_corpus
from influence_graph import influence_graph
import matplotlib.pyplot as plt
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
    for key in igraph.edge[e[0]][e[1]]['weights']:
        temp_weight += igraph.edge[e[0]][e[1]]['weights'][key]
    if temp_weight > max_edge_weight:
        max_edge = e
        max_edge_weight = temp_weight
print "Most related node pair",max_edge," with weight",max_edge_weight
#Visualize path between nodes in max_edge
descendants0 = nx.descendants(graph,max_edge[0])
descendants0.add(max_edge[0])
descendants1 = nx.descendants(graph,max_edge[1])
descendants1.add(max_edge[1])

common_desc = descendants0.intersection(descendants1)
print "Common descendants of ",max_edge," are: ",common_desc


nx.draw(graph)
plt.show()
