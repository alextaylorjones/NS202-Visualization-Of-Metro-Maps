#!/usr/env/python
import networkx as nx
import glob

class load_corpus:
    """A class for loading one or more citation corpus, extracting the metadata from the .abs files 
    and constructing the citation DAG"""
    network_dict = {};
    def __init__(self, file_dir_name, cit_file_name, name, max_size = 40000):
        print "Loading files from:",file_dir_name,"into network ", name

        #Call helper fuction to parse citation network
        assert(name != None)

        #Get network from citation file, limiting size by max size
        net = self.parse_citation_network(cit_file_name,file_dir_name, max_size)
        if (net != None):
            self.network_dict[name] = net
        else:
            print "Network returned null, no network created"


    """Reads graph with name == g_name from network dictionary"""
    def read_graph(self,g_name):
        print "Reading graph \'",name,"\' from memory"

        #Find named network in class variables
        if (name in self.network_dict):
            net = self.network_dict[name];
            print "Network loaded : nodes (",len(net),") , edges(",len(net.edges()),")"
            return net
        else:
            print "No network by that name or network not loaded"
            return None

    """ Helper function to parse tab-seperated citation file, up to max_size edge entries""" 
    def parse_citation_network(self,cit_file_name,directory, max_size):
        #Initialize DAG to load citation edges into
        graph = nx.DiGraph();
        full_filename = ""
        full_filename += directory
        full_filename += cit_file_name
        print "Parsing citation file : '\'", full_filename,"\'"
        try:
            f = open(full_filename,'r')
            for i,line in enumerate(f):
                #Strip comments
                if (line[0] == "#"):
                    continue
                line = line.rstrip('\r\n')
                items = line.split('\t')
                assert(len(items) == 2)
                if (items[0] in graph) == 0:
                    node_dict = self.read_metadata(directory,items[0])
                    graph.add_node(items[0], time = node_dict['time'], abstract = node_dict['abstract'], author = node_dict['author'])
                    
                if (items[1] in graph) == 0:
                    graph.add_node(items[1])
                    node_dict = self.read_metadata(directory,items[1])
                    graph.add_node(items[1], time = node_dict['time'], abstract = node_dict['abstract'], author = node_dict['author'])
                    

                graph.add_edge(items[0],items[1])

            
                #Step if reached max number of edges to add.
                if (i > max_size):
                    break
            print graph.nodes()
            x=raw_input()
            return graph
        except:
            print "Exception thrown in loading citation file, ", full_filename
            return None
        """Find file_id.abs in directory specified, returning a dict with following metadata:
            title, abstract,time,author"""
        def read_metadata(self,directory,file_id):
            local_name = ""
            local_name += file_id
            local_name += '.abs'
            file_name = self.find(local_name,directory)

            # Must find file, or throw an error
            assert(file_name != None)

        def find(name, path):
            for root, dirs, files in os.walk(path):
                if name in files:
                    return os.path.join(root, name)

