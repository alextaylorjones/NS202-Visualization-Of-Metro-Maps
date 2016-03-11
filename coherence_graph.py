#!/usr/env/python
import networkx as nx
from heapq import heappush,heappop
import random as rand

class coherence_graph:
    influence_graph = None 
    active_concepts = None
    threshold_num_chains = None
    m_chain_length = None
    min_coherence = None
    cohGraph = None
    sample_dist = None

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
            #print "pushing node",node," to heap"
            heappush(q,(-10,[node]))
            num_chains += 1


        while num_chains < self.threshold_num_chains:
            if (len(q)) == 0:
                #print "Out of choices to pop from heap"
                break
            best_choice = heappop(q)

            #print best_choice, "is popped val"
            best_chain = best_choice[1]
            #print type(best_chain),"is type of chain of length ", len(best_chain)

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
                #if (num_ext == 0):
                
                    #print "No more extensions possible"
                    #break
        print "Done computing chains"
            #Now convert nodes in coherence graph into paths, linking paths at all intersecting nodes
        for chain in chain_list:
            print str(chain), "coherence - ",self.calc_coherence(chain)
            cohGraph.add_node(tuple(chain))

        for chain in chain_list:
            for other_chain in chain_list:
                if (chain != other_chain):
                    if chain[1:] == other_chain[:-1]:
                        #print "Overlap",str(chain), " and ",other_chain
                        cohGraph.add_edge(tuple(chain),tuple(other_chain))
                    if other_chain[1:] == chain[:-1]:
                        #print "Overlap",chain, " and ",other_chain
                        cohGraph.add_edge(tuple(other_chain),tuple(chain))
        print "Num overlaps (Edges)",len(cohGraph.edges()), "num chains :",len(cohGraph.nodes())

        #Make sure construction made no loops
        assert(len(list(nx.simple_cycles(cohGraph))) == 0)
        #Save copy to class variable
        self.cohGraph = cohGraph
        #Set node attribute
        nx.set_node_attributes(self.cohGraph, 'walk-tally',0)

    #Helper
    def get_coherence_graph(self):
        return self.cohGraph
    def get_influence_graph(self):
        return self.influence_graph


    #Weight coherent paths according to random walks starting at p_start in coherence graph
    #Use related param to start portion of walks at related papers (higher means more likely to start at related nodes)
    def randomly_sample_coherent_paths(self,p_start,num_samples, related_param):
      #Find related papers in the influence graph
      #Weight according to sum of influence graph edge scores
      edge_sum = 0
      related_paper_dict = {}
      for neighbor in self.influence_graph.neighbors(p_start):
        edge_sum += sum([self.influence_graph.edge[p_start][neighbor]['weights'][c] for c in self.active_concepts])
        #print "p_start has influence of ", edge_sum, "with neighbor " , neighbor
        related_paper_dict[neighbor] = edge_sum

      self.setup_random_dict_for_sampling(related_paper_dict)
      #Sample chains in cohGraph
      for s in range(num_samples):
        if (rand.random() < related_param):
          #get_rand_related_paper
          related_paper = self.sample_dict_randomly()
          #print "Walking from",related_paper
          self.tally_walk_from(related_paper)
        else: #start at p_start
          #print "Walking from ",p_start
          self.tally_walk_from(p_start)

  
      #Add atribute to influence graph for coverage
      nx.set_node_attributes(self.influence_graph, 'coverage',0)

      #Collect walk tallies for all chains, sum and add to nodes in the influence graph
      for chain in self.cohGraph.nodes():
        print "Chain:",chain," - ",self.cohGraph.node[chain]['walk-tally']/float(num_samples)
        for node in chain:
          self.influence_graph.node[node]['coverage'] += self.cohGraph.node[chain]['walk-tally']

      #DEBUG
      #for node in self.influence_graph.nodes():
      #  print "Node:",node," coverage score ",self.influence_graph.node[node]['coverage']

  #Walk from node in coherence graph
    def tally_walk_from(self,start):
      starting_list = []
      #since coherence graph is store in chains, find all instances of a node in chain list
      for node in self.cohGraph:
          if str(start) in node:
              starting_list.append(node)

      if (len(starting_list) == 0):
        #DEBUG
        #print "Empty list of chains to walk from for paper",start
        return

      #Randomly select cohe)rence subchain to start at
      cur = rand.choice(starting_list)
      while len(list(self.cohGraph.neighbors(cur))) > 0:
          #Update tally
          self.cohGraph.node[cur]['walk-tally'] += 1
          #Randomly walk to a neighbor
          #print self.cohGraph.neighbors(cur),"neighbors"
          cur =rand.choice(self.cohGraph.neighbors(cur))

    #Setup given dict for random sampling uniformly in proportion to weight given by dict
    def setup_random_dict_for_sampling(self,node_weight_dict):
        nodes = [key for key in node_weight_dict.keys()]
        self.sample_dist = []
        #Sum edge totals
        cm_sum = sum([node_weight_dict[key] for key in node_weight_dict.keys()])
        cm = 0
        for i,n in enumerate(nodes):
            cm += node_weight_dict[n]/float(cm_sum)
            self.sample_dist.append( (n,cm))

    def sample_dict_randomly(self):
        r = rand.random()
        for (entry,prob) in self.sample_dist:
            if r < prob:
                return entry
        print "Error in sampling"
        return self.sample_dist[-1]

    def rank_dag_according_to_coverage(self,dag):
      scores = {node: self.influence_graph.node[node]['coverage'] for node in dag.nodes()}
      sorted_scores = sorted(scores.items(),key=lambda x: x[1],reverse=True)
      nx.set_node_attributes(dag,'coverage',0)
      i = 0
      for node,score in sorted_scores:
        dag.node[node]['coverage'] = i
        i += 1
      return dag
