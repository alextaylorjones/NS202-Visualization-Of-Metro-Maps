#!/usr/env/python
import networkx as nx
graph = nx.read_gml("stanford-hepth_citation.gml")
#igraph = nx.read_gml("stanford-hepth_influence.gml")
for e in igraph.edges():
    print e, igraph.edge[e[0]][e[1]]
