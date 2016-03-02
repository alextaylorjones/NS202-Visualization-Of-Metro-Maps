import networkx as nx
from load_corpus import load_corpus
from influence_graph import influence_graph
#Load a corpus into memory
loader = load_corpus('/home/alex/classes/NS202/project/NS202-METRO-MAP-VISUALIZATION-OF-CITATION-NETWORKS/datasets/','Cit-HepTh.txt','stanford-hepth',250)
#Get the loaded graph
graph = loader.get_graph('stanford-hepth')

#Create the influence graphs based 
#hardcoded concepts for now
concepts = ['boson','symmetry','SO']
influence = influence_graph(graph, concepts)
influence.construct_influence_graph(loader.get_author_dict())
influence.visualize_concept_graph('SO')
