import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import math
import re
from pdb import set_trace as bp

class influence_graph:
    citation_graph = None
    concepts = None
    concept_graph = None
    influence_graph = None

    def __init__(self,graph, _concepts):
        self.citation_graph = graph
        self.concepts = _concepts
        self.concept_graph = nx.DiGraph()
        self.influence_graph = nx.Graph()

        for e in graph.edges():
            self.concept_graph.add_edge(e[0],e[1],weights = dict((c,0) for c in _concepts))

        for u in graph.nodes():
          for v in graph.nodes():
            if (u == v):
              continue
            self.influence_graph.add_edge(u,v,weights = dict((c,0) for c in _concepts))

    def reset_concepts(self,concepts):
        self.concepts = concepts
        nx.set_edge_attributes(self.influence_graph,'weights',{})
        nx.set_edge_attributes(self.concept_graph,'weights',{})

        for e in self.concept_graph.edges():
            for c in concepts:
                self.concept_graph.edge[e[0]][e[1]]['weights'][c] = 0

        for u in self.influence_graph.nodes():
            for v in self.influence_graph.nodes():
                if (u == v):
                    continue
                for c in concepts:
                    self.influence_graph.edge[u][v]['weights'][c] = 0

    """ Call this once on a set of concepts to construct the influence graph from the concepts """
    def construct_influence_graph(self,author_dict):
        # Create a concept graph for each inputted concept
        #Using the concepts
        #Calculate the frequencies of all concepts in the abstracts and total document length
        #Add statistics to node attributes
        for v in self.citation_graph.nodes():
            concepts_matched = 0
            self.citation_graph.node[v]['concept_freq'] = {}
            for c in self.concepts:
                #Case insensitive match using re.findall
                reg_ex = "(?i)"
                reg_ex += c
                concept_match_num  = len(re.findall(reg_ex,self.citation_graph.node[v]['abstract']))
                concept_dict = self.citation_graph.node[v]['concept_freq']
                concept_dict[c] = concept_match_num
                concepts_matched += concept_match_num
            #print "Concept freq(",self.citation_graph.node[v]['file_name'],"): ",self.citation_graph.node[v]['concept_freq'], "total - ", concepts_matched
            self.citation_graph.node[v]['doc_length'] = concepts_matched

       #Use node attributes to create an influence graph
       #Using notation from BEyond Keyword Search 2010
        for y in self.citation_graph.nodes():
            #Get the papers that y cited 
            y_out_edges = self.citation_graph.out_edges(y)
            #print y,y_out_edges
            #x=raw_input()
            y_cited = [e[1] for e in y_out_edges]
            if len(y_cited) == 0:
                #print "",y," has no citations in the network"
                continue
            #Get previous papers written by author of y using helper methods
            prev_papers = self.get_previously_written_papers(y,author_dict)
            l = 0
            if (prev_papers != None):
                l = len(prev_papers)
            Z = {}

            """ Comments on Method:
                In this method, any paper which does not explicitly name a concept in the concept list will have zero edge weight in the influence graph, and so we do not need to add this edge at all.
            """
            #Calculate Z
            #TODO : make more efficient in terms of lines of code
            #note: we use Z to normalize weights for concept graph
            for c in self.concepts:
                #Sum over all cited papers of concept c frequency / doc length
                sum_nrj = 0
                for cited in y_cited:
                    sum_nrj += float(self.citation_graph.node[cited]['concept_freq'][c]) / (self.citation_graph.node[cited]['doc_length'] + 1)

                #Sum over all coauthored (prev) papers
                if (l > 0):
                    #Sum over all prev papers of concept c frequency /doc length
                    sum_nbj = 0
                    for coauth in prev_papers:
                        sum_nrj += float(self.citation_graph.node[coauth]['concept_freq'][c]) / (self.citation_graph.node[coauth]['doc_length'] + 1)
                #Novelty cost assumed 0 for now
                #TODO: update
                novel_c = 0.0
                if (l >0 ):
                    Z[c] = sum_nrj + (1/len(prev_papers))*sum_nbj + novel_c
                else:
                    Z[c] = sum_nrj + novel_c

                # No concept c found in y_cited, no need to add to concept graph, Since weight for edge will be 0
                #Note: if we care about this data, regardless of edge weight, then we may include it in graph with 0 weight(not implemented here)
            #TODO: undo hack of 'doc_length' +1 to account for no concept match in abstract
            #Calculate the weight of each concept for the edges in the citation graph
            for ri in y_cited:
                self.concept_graph.add_edge(ri,y, weights = {})

                for c in self.concepts:
                    if Z[c] != 0:
                        self.concept_graph[ri][y]['weights'][c] = (1/Z[c])*float((self.citation_graph.node[ri]['concept_freq'][c]))/(self.citation_graph.node[ri]['doc_length']+1)
                    if Z[c] == 0:
                        self.concept_graph[ri][y]['weights'][c]  = 0

            #Calculate the weight of each concept from previously authored papers, if they exist
            if l > 0:
                for bi in prev_papers:
                        if (bi == y):
                            print "Self is previous paper"
                            continue
                        self.concept_graph.add_edge(bi,y, weights = {})
                        for c in concepts:
                            if Z[c] == 0:
                                self.concept_graph[bi][y]['weights'][c]  = 0
                            if Z[c] != 0:
                                self.concept_graph[bi][y]['weights'][c] = (1/(Z[c] * len(prev_papers)))*(float(self.citation_graph.node[bi]['concept_freq'][c]))/(self.citation_graph.node[bi]['doc_length']+1)


        #Sanity check
        #print "Check Weights for edges in concept graph"
        #for v in self.concept_graph.edges():
        #    print " ->", self.concept_graph[v[0]][v[1]]['weights'],v

    """ Find papers in citation network which have the same author as y but came before y"""
    def get_previously_written_papers(self,y, author_dict):
        prev_papers= []
        authors = self.citation_graph.node[y]['authors'].split(',')
        #print self.citation_graph.node[y]['authors']
        #print authors[:], " are authors"

        for auth in authors:
            #print "Getting all previously written papers by", auth
            for p in author_dict[auth]:
                if p not in self.citation_graph:
                  #print p," not in citation graph."
                  continue
                if y not in self.citation_graph:
                  #print y," not in citation graph."
                  continue
                if self.citation_graph.node[p]['year'] < self.citation_graph.node[y]['year']:
                    #print "Adding ", p, " to previous papers list"
                    prev_papers.append(p)
                elif (self.citation_graph.node[p]['year'] == self.citation_graph.node[y]['year']) and (self.citation_graph.node[p]['date'] < self.citation_graph.node[y]['date']):
                    #print "Adding ", p, " to previous papers list"
                    prev_papers.append(p)

            #print auth, " has ",prev_papers[:]

    """ Note: this is slow and should be called in preprocessing
        use the function load_document_pairs(filename) below to load """
    """Compute pairwise document influences for each concept, using closeness to real value (delta)
    to generate sample number"""
    def compute_document_pair_influences(self,delta):
        #See thm 1 - Beyond Keyword Influence
        num_samples =int( math.ceil((2/delta*delta)*math.log((len(self.concept_graph.nodes()*(len(self.concept_graph.nodes())-1))/delta) )))
        print "Using ", num_samples," graph samples to compute pairwise differences"

        for c in self.concepts:

            all_pairs_descendant_count = {}

            #Compute graph samples and take influence readings
            for x in range(num_samples):

                #Uniformly sample edges of concept graph according to weight of egdes of type c
                sample = self.sample_concept_graph(c)

                for u in sample.nodes():
                    for v in sample.nodes():
                        # Only use (u,v) pairs so as to not double count
                        if (u == v or (v,u) in all_pairs_descendant_count):
                            continue

                        #Setup dictionary entry
                        if ( (u,v) not in all_pairs_descendant_count):
                            all_pairs_descendant_count[(u,v)] = 0

                        #First approach, using nx libs, slow but it works
                        #
                        descendants_u = nx.descendants(sample,u)
                        descendants_v = nx.descendants(sample,v)
                        descendants_u.add(u)
                        descendants_v.add(v)

                        #Look for one common descendants, break and add to count if found
                        common_desc_found = 0
                        for desc in descendants_u:
                            if desc in descendants_v:
                                common_desc_found = 1
                                break
                        if common_desc_found == 1:
                            all_pairs_descendant_count[(u,v)] = all_pairs_descendant_count[(u,v)] + 1

            #Iterate through all pairs and add weights to the influence graph (wrt to concept c)
            for u,v in all_pairs_descendant_count.keys():
                #Add u,v weight wrt concept c according to number of samples counted that had a common descendant
                self.influence_graph.edge[u][v]['weights'][c] = float(all_pairs_descendant_count[(u,v)]) / num_samples
                #print "Node pair ",(u,v)," has weight ", float(all_pairs_descendant_count[(u,v)]) / num_samples, "wrt to concept (",c,")."

        #end for (concept loop)

    def sample_concept_graph(self,concept):
        sample = nx.DiGraph()
        for e in self.concept_graph.edges():
            #print "Sampling edge",e," : weight ",self.concept_graph[e[0]][e[1]]['weights'][concept]
            if rand.random() < self.concept_graph[e[0]][e[1]]['weights'][concept]:
                sample.add_edge(e[0],e[1])
                #print "Edge sampled!"
        return sample

    def load_document_pair_influences(self,filename):
        print "empty"
    def get_influence_graph(self):
        return self.influence_graph
