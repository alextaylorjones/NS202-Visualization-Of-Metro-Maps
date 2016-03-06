#!/usr/bin/python
import networkx as nx

class tree_intersection:

    def __init__(self):
        print "Tree intersection initialize"

    """ Compute the intersection between the ancestors of new_node
    and the descendents of old_node  in a DAG"""
    def get_intercitation_dag(self,old_node, new_node, dag):
       # Compute necessary lineages
        desc = nx.descendants(dag,old_node)
        desc.add(old_node)
        anc = nx.ancestors(dag,new_node)
        anc.add(new_node)

        # Intersect lineages to get ad tree
        intersect = desc.intersection(anc)

        if (len(intersect) == 0):
            print "No common intercitations between ",old_node," and ",new_node
        else:
            #Compute all from old_node to intersect
            intercite_dag = nx.DiGraph()
            for dag_node in intersect:

                #Iterate through all paths from old node to target
                for path in nx.all_simple_paths(dag,source=old_node,target=dag_node):
                    for i,node in enumerate(path):
                        if (i < len(path)-1):
                           intercite_dag.add_edge(path[i],path[i+1])

                        
                for path in nx.all_simple_paths(dag,source=dag_node,target=new_node):
                    for i,node in enumerate(path):
                        if (i < len(path)-1):
                           intercite_dag.add_edge(path[i],path[i+1])

            return intercite_dag
