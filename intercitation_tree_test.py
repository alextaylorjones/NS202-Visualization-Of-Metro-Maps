import networkx as nx
from tree_intersection import TreeIntersection
from load_corpus import load_corpus
from influence_graph import influence_graph
from coherence_graph import coherence_graph
import matplotlib.pyplot as plt

#Load a corpus into memory
loader = load_corpus('./datasets/','Cit-HepTh.txt','stanford-hepth',5000)
citegraph = loader.get_graph('stanford-hepth')

#Get influence graph
concepts = ['string', 'SO','type IIA','type IIB']
influence = influence_graph(citegraph, concepts)
influence.construct_influence_graph(loader.get_author_dict())
influence.compute_document_pair_influences(0.08)
igraph = influence.get_influence_graph()


ti = TreeIntersection()

print "Cycles",len(list(nx.simple_cycles(citegraph)))

pl_max = -1
longest_dist_pair = None
concept_max = -1
u_max = None
for u in igraph.nodes():
  concept_rel = 0
  for neighbors in igraph.neighbors(u):
    concept_rel += sum([igraph.edge[u][neighbors]['weights'][c] for c in concepts])
  if concept_rel > concept_max:
    concept_max = concept_rel
    u_max= u

for v in citegraph.nodes():
  if (nx.has_path(citegraph,u_max,v)):
    pl = nx.dijkstra_path(citegraph,u_max,v)
    if (len(pl)>1):
        pl = len(pl)
        if pl > pl_max:
            pl_max = pl
            longest_dist_pair = (u_max,v)
            print "Longer pair", (u_max,v)," with len",pl

  if (nx.has_path(citegraph,v,u_max)):
    pl = nx.dijkstra_path(citegraph,v,u_max)
    if (len(pl)>1):
        pl = len(pl)
        if pl > pl_max:
            pl_max = pl
            longest_dist_pair = (v,u_max)
            print "Longer pair", (v,u_max)," with len",pl






intercite = (ti.get_intercitation_dag(longest_dist_pair[0],longest_dist_pair[1],citegraph))

intercite = ti.add_relevant_citing_nodes(intercite,citegraph,0.1)
#Fill in citations more fully with all in and outneighbors in intercite graph
#intercite = ti.add_cited_citing_nodes(intercite,citegraph)

if intercite != None:
    print "Intercite (,",u,",",v," - ",len(intercite)


#Compute coherence chains
NUM_CHAINS = 4000
MIN_LENGTH_CHAIN = 5
MIN_COHERENCE = 0.01
cohG = coherence_graph(igraph,concepts,NUM_CHAINS,MIN_LENGTH_CHAIN,MIN_COHERENCE)

#Create a coherence graph on the intercited graph
cohG.greedy_coherence_graph_create(intercite)

#Weight nodes in the coherence graph according to appearance on walks that 
#start at longest_dist_pair[0]
NUM_SAMPLES = 3000
RELATED_PARAM = 0.0
cohG.randomly_sample_coherent_paths(longest_dist_pair[0],NUM_SAMPLES,RELATED_PARAM)

#NOTE: we are getting the influence graph because it contains all the weighted coverage values
coverage_weighted_inf_graph = cohG.get_influence_graph()



pos=nx.spring_layout(citegraph) # positions for all nodes

# nodes
nx.draw_networkx_nodes(citegraph,pos,
                       nodelist=citegraph.nodes(),
                       node_color='r',
                       node_size=50,
                   alpha=0.1)

total_coverage = sum([coverage_weighted_inf_graph.node[x]['coverage'] for x in coverage_weighted_inf_graph.nodes()])
max_coverage = max([coverage_weighted_inf_graph.node[x]['coverage'] for x in coverage_weighted_inf_graph.nodes()])
for x in intercite.nodes():
    col =  coverage_weighted_inf_graph.node[x]['coverage'] /float(total_coverage)
    if (col*float(total_coverage) > max_coverage/2.0):
        col = 1.0
        print "col is high enought",col

        nx.draw_networkx_nodes(citegraph,pos,node_list=x,node_color=[0,col,0]  )
    else:
        nx.draw_networkx_nodes(citegraph,pos,node_list=x,node_color=[0,col,0]  )
        
    #nx.draw_networkx_nodes(citegraph,pos,
    #                       nodelist=list(str(node)),
    #                       node_color=[0,0,255*(coverage_weighted_inf_graph.node[node]['coverage']/float(total_coverage))],
    #                       node_size=500,
    #                        alpha=1)

# edges
nx.draw_networkx_edges(citegraph,pos,
                       edgelist=citegraph.edges(),
                       width=8,alpha=0.1,edge_color='r')
nx.draw_networkx_edges(citegraph,pos,
                       edgelist=intercite.edges(),
                       width=8,alpha=0.8,edge_color='b')
plt.show()
