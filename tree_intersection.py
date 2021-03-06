#!/usr/bin/python
import networkx as nx
import math
import operator

class TreeIntersection:

    def __init__(self):
        print "Tree intersection initialize"

    #def set_params(self,focus_network,focus_content,importance,diversity,jumpiness,coherence):

    def get_parameterized_intercitation_dag(self,old_node,new_node,dag):
        desc = nx.descendants(dag,old_node)
        desc.add(old_node)
        anc = nx.ancestors(dag,new_node)
        anc.add(new_node)

        # Intersect lineages to get ad tree
        intersect = desc.intersection(anc)

        if (len(intersect) == 0):
            print "No common intercitations between ",old_node," and ",new_node
        else:
          rev_dag = nx.reverse(dag,copy=True)
          # Strength of weighting due to impact (# citations)
          impact_param = 1.0

          #Strength of weighting due to network relevance of paper's citations
          network_relevance_param = 1.0

          #Strength of weighting due to redundancy in citation network
          network_robustness_param = 1.0

          sum_citations = sum([pow(dag.in_degree(w),impact_param) for w in intersect])

          #Store importance score
          importance_dict = {}
          for w in intersect:
            importance_dict[w] = pow(dag.in_degree(w),impact_param)

          #Calculate network relevance
          net_relevance = {}
          for w in intersect:
            cited_reach_cnt = 0
            for cited in dag.neighbors(w):
              #If we can reach old node through cited node add to count
              if (nx.has_path(dag,cited,old_node)):
                cited_reach_cnt += 1
            net_relevance[w] = pow(float(cited_reach_cnt)/dag.out_degree(w),network_relevance_param)


          #Calculate network robustness
          net_robustness = {}
          for w in intersect:
            citer_alt_path = 0
            cited_alt_path = 0
            for citer in rev_dag.neighbors(w):
              #If we can reach old node through citer node (without using that citation as a link)
              if (nx.has_path(dag,citer,old_node)):
                citer_alt_path += 1
            for cited in dag.neighbors(w):
              if (nx.has_path(rev_dag,cited,new_node)):
                cited_alt_path += 1
            net_robustness[w] = pow(float(cited_alt_path + citer_alt_path)/(dag.out_degree(w) + dag.in_degree(w)),network_robustness_param)
          #Now we have ranked all the intersect nodes, build paths according to weights of each node


    """ Compute the intersection between the ancestors of new_node
    and the descendents of old_node  in a DAG"""
    def get_intercitation_dag(self,old_node, new_node, dag):
        print "getting intercitation dag"
        # print dag.nodes()
       # Compute necessary lineages
        desc = nx.descendants(dag,old_node)
        desc.add(old_node)
        anc = nx.ancestors(dag,new_node)
        anc.add(new_node)
        #
        # print "descendants: "
        #
        # print desc
        # print "ancestors: "
        # print anc

        # Intersect lineages to get ad tree
        intersect = desc.intersection(anc)
        # print "Intersection: ", intersect
        if (len(intersect) == 0):
            print "No common intercitations between ",old_node," and ",new_node
        else:
            #Compute all from old_node to intersect
            intercite_dag = nx.DiGraph()
            for dag_node in intersect:
                #Iterate through all paths from old node to target
                for path in nx.all_simple_paths(dag,source=old_node,target=dag_node, cutoff=int(1.5*nx.shortest_path_length(dag,old_node,dag_node))):
                    #print "path",path
                    #print path
                    for i,node in enumerate(path):
                        #print i
                        if (i < len(path)-1):
                           intercite_dag.add_edge(path[i],path[i+1])
                for path in nx.all_simple_paths(dag,source=dag_node,target=new_node, cutoff=int(1.5*nx.shortest_path_length(dag,old_node,dag_node))):
                    #print "path2",path
                    for i,node in enumerate(path):
                        #print i
                        if (i < len(path)-1):
                           intercite_dag.add_edge(path[i],path[i+1])

            # print "Intercite notes",intercite_dag.nodes()
            # x=raw_input()
            return intercite_dag

    def add_cited_citing_nodes(self,dag, citegraph):
      """ Take original subgraph of cite graph - dag and add to it all in and out neighbors """
      fuller_dag = nx.DiGraph()
      rev_cite = nx.reverse(citegraph,copy=True)
      for node in dag.nodes():
        for neighbor in citegraph.neighbors(node):
          fuller_dag.add_edge(node,neighbor)
        for in_neighbor in rev_cite.neighbors(node):
          fuller_dag.add_edge(in_neighbor,node)

      assert(len(list(nx.simple_cycles(fuller_dag))) == 0)

      return fuller_dag

    #Find papers in the citagraph which heavily cite the papers in dag
    def add_relevant_citing_nodes(self,dag,citegraph, percentage_rank):
        rev_citegraph = nx.reverse(citegraph, copy=True)
        cite_relevance_dict = {}
        citers_relevance_dict = {}
        if dag == None:
          print "No itersection dag"
          return dag
        for node in citegraph:
            cited = set(citegraph.neighbors(node))
            if len(cited) == 0:
                continue

            cite_relevance_dict[node] = -float( len(cited.intersection(set(dag.nodes()))) /len(cited))

        for node in citegraph:
            citers = set(rev_citegraph.neighbors(node))
            if len(citers) == 0:
                continue
            citers_relevance_dict[node] = -float( len(citers.intersection(set(dag.nodes()))) /len(citers))

        sorted_cite_relevance = sorted(cite_relevance_dict.items(),key =operator.itemgetter(1))

        sorted_citer_relevance = sorted(citers_relevance_dict.items(),key =operator.itemgetter(1))

        print sorted_cite_relevance ,sorted_citer_relevance
        for x in range(int(percentage_rank*len(sorted_cite_relevance))):
            if x < len(sorted_cite_relevance) -1:
                node_to_add = sorted_cite_relevance[x]
                for neigh in citegraph.neighbors(node_to_add[0]):
                    if neigh in dag.nodes():
                        dag.add_edge(node_to_add[0],neigh)
                        print "adding edge",(node_to_add[0],neigh)


        for x in range(int(percentage_rank*len(sorted_citer_relevance))):
            if x < len(sorted_citer_relevance) -1:
                node_to_add = sorted_citer_relevance[x]
                for neigh in rev_citegraph.neighbors(node_to_add[0]):
                    if neigh in dag.nodes():
                        dag.add_edge(neigh,node_to_add[0])
                        print "adding edge",(neigh,node_to_add[0])
        return dag

