#!/usr/env/python
import networkx as nx
from heapq import heappush,heappop
class coherence_graph:
    influence_graph = None 
    active_concepts = None
    threshold_num_chains = None
    m_chain_length = None
    min_coherence = None

    def __init__(self,influence_graph,active_concepts, threshold_num_chains, min_length_chain, min_coherence):
        print "Initializing coherence graph"
        self.influence_graph = influence_graph
        self.active_concepts = active_concepts
        self.threshold_num_chains = threshold_num_chains
        self.m_chain_length = min_length_chain
        self.min_coherence = min_coherence

    def calc_coherence(self,chain):
        coh  = 100000
        min_coh = 100000
        for i,c in enumerate(chain):
            if i < len(chain) - 1:
                coh = 0
                for concept in self.active_concepts:
                    #if (self.influence_graph.edge[c][chain[i+1]] != None):
                    coh += self.influence_graph.edge[c][chain[i+1]]['weights'][concept]
                min_coh = min(coh,min_coh)
        #print "Calc coherence from chain",chain, " = ",min_coh
        return -min_coh

    """ Create a coherence graph on the dag provided """
    def greedy_coherence_graph_create(self,dag):
        q = []
        cohGraph = nx.DiGraph()
        rev_dag = nx.reverse(dag,copy=True)
        chain_list = []
        num_chains = 0
        #Add all nodes to priority queue
        for node in dag.nodes():
            #All nodes have initially 0 coherence as chains
            print "pushing node",node," to heap"
            heappush(q,(-10,[node]))
            num_chains += 1


        while num_chains < self.threshold_num_chains:
            if (len(q)) == 0:
                print "Out of choices to pop from heap"
                break
            best_choice = heappop(q)

            print best_choice, "is popped val"
            best_chain = best_choice[1]
            print type(best_chain),"is type of chain of length ", len(best_chain)

            # If chain is long enough, turn it into a vertex of G
            if len(best_chain) >= self.m_chain_length:
                chain_list.append(best_chain)
                num_chains += 1
            else:
                #Generate all extensions of best_Choice and add to queue
                #print "Generating all extensions of ",best_chain
                #x=raw_input()
                #Get last element of chain
                last_ele = best_chain[-1]

                #All extensions
                num_ext = 0

                for i,ext in enumerate(rev_dag.neighbors(last_ele)):
                    if (ext in best_chain):
                        continue
                    #print "Adding to chain",best_chain, " with ",ext

                    new_chain = best_chain[:]
                    new_chain.append(ext)
                    #print "Adding new chain as extension",new_chain
                    chain_coherence= self.calc_coherence(new_chain)
                    if (chain_coherence < -self.min_coherence):
                        heappush(q,(chain_coherence,new_chain))
                        num_ext += 1
                if (num_ext == 0):
                    print "No more extensions possible"
                    #break
        print "Done computing chains"
            #Now convert nodes in coherence graph into paths, linking paths at all intersecting nodes
        for chain in chain_list:
            print chain, "coherence - ",self.calc_coherence(chain)
