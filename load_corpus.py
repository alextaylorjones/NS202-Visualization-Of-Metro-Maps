#!/usr/env/python
import networkx as nx
import glob
import sys
import os
import re

class load_corpus:
    """A class for loading one or more citation corpus, extracting the metadata from the .abs files 
    and constructing the citation DAG"""
    network_dict = {}
    author_dict = {}
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

    def get_author_dict(self):
        return self.author_dict
    """Save  a named graph in file_with the name provided""" 
    def save_graph(self,file_name, graph_name):
        nx.write_gml(self.network_dict[graph_name], file_name)


    """Reads graph with name == g_name from network dictionary"""
    def get_graph(self,g_name):
        print "Reading graph \'",g_name,"\' from memory"

        #Find named network in class variables
        if (g_name in self.network_dict):
            net = self.network_dict[g_name];
            print "Network loaded : nodes (",len(net),") , edges(",len(net.edges()),")"
            return net
        else:
            print "No network by that name or network not loaded"
            return None
    """Find file_id.abs in directory specified, returning a dict with following metadata:
        title, abstract,time,author"""
    def read_metadata(self,directory,file_id):
        local_name = ""
        local_name += file_id.rjust(7,'0')
        local_name += '.abs'
        #Read directory and filename
        find_array = self.find(local_name,directory)
        if (str(local_name)[0] == '0'):
            file_year = int('20' + str(local_name)[0:2])
        elif (str(local_name)[0] == '9'):
            file_year = int('19' + str(local_name)[0:2])
        else:
            print "incorrect file naming convention",local_name
        file_name = find_array[1]
        meta_dict = {}

        meta_dict['file_id'] = file_id
        meta_dict['file_name'] = file_name

        assert(file_name != None)
        #TODO: make more general, not just for stanford HepTh dataset
        #try:
        f = open(file_name,'r')
        section_flag = 0
        abstract = ""
        for i, line in enumerate(f):
            #IF section flag is 2, read abstract
            if '\\\\' in line:
                #If first \\ encountered, then metadata is in next lines
                if section_flag == 0:
                    #print "encountering metadata"
                    section_flag = 1
                    continue
                #If second \\ encountered, then abstract follows until end of file
                elif section_flag == 1:
                    #print "moving to abstract"
                    section_flag =2
                    continue
                elif section_flag == 2:
                    #print "Completed reading file: ",file_name
                    break

            if section_flag == 2:
                #print "Reading line into abtract ",line
                abstract += line.replace('\n', ' ' )
                continue
            if section_flag == 1:
                items = line.split(':')
                if items[0] == "Date":
                    #provisional attempt
                    #dates are non-standard format, but all have the month as the final three 
                    month_candidates = re.findall("[a-zA-Z]{3}",items[1])
                    ms = str(month_candidates[-1:][0] )
                    for month_cand in month_candidates:
                      month = self.month_to_num(ms)
                      if (month != -1):
                        break
                      else:
                        print line, month_cand, "not a month"
                    if (month == -1):
                      print "Inconsistency in dating file", file_name, " @ ",line
                      month = 1
                    meta_dict['date'] = month
                    meta_dict['year'] = file_year
                if items[0] == "Title":
                    #print items[1]
                    meta_dict['title'] = items[1]

                if items[0] == "Author" or items[0] == "Authors":
                    #print "Authors line: ", line
                    line.strip('\r\n')
                    author_split = items[1].split(',')
                    authors = []
                    for count,item in enumerate(author_split):
                        #print item, "item -> #",count
                        item = item.strip('\n')
                        if item == ' ' or item == '':
                            #print "Empty"
                            continue
                        if (" and " not in item):
                            authors.append(item)
                            #print "Author:", item
                            #print "Adding paper ",file_id," to authorship list"
                            #Add author 
                            if (item not in self.author_dict):
                                self.author_dict[item] = [file_id]
                            else:
                                self.author_dict[item].append(file_id)
                        else:
                            last_two_auth = item.split(' and ')
                            #print "last two authors",last_two_auth[:]
                            if (len(last_two_auth) != 2):
                                print "Last two authors not of length 2:, ",line
                                authors.append("missing")
                                break
                            assert(len(last_two_auth) == 2)
                            authors.append(last_two_auth[0])
                            authors.append(last_two_auth[1])
                            #Author 1
                            #print "Author:", last_two_auth[0], "Adding paper ",file_id," to authorship list"
                            if (last_two_auth[0] not in self.author_dict):
                                self.author_dict[last_two_auth[0]] = [file_id]
                            else:
                                self.author_dict[last_two_auth[0]].append(file_id)

                            #Author 2
                            #print "Author:", last_two_auth[1], "Adding paper ",file_id," to authorship list"
                            if (last_two_auth[1] not in self.author_dict):
                                self.author_dict[last_two_auth[1]] = [file_id]
                            else:
                                self.author_dict[last_two_auth[1]].append(file_id)
                    meta_dict['authors'] = ""
                    for i,a in enumerate(authors):
                        meta_dict['authors'] += a
                        if len(authors) - 1 > i:
                            meta_dict['authors'] += ','
                    #print meta_dict['authors']

                    #print authors[:]
        #After while loop is finished, save all text in abstract string
        meta_dict['abstract'] = abstract

        if 'authors' not in meta_dict.keys():
            meta_dict['authors'] = "missing"

        return meta_dict
        #except:
        #    print "Error opening",file_name
        #    print "Unexpected error:", sys.exc_info()[:]
    """ Helper function to parse tab-seperated citation file, up to max_size edge entries""" 
    def parse_citation_network(self,cit_file_name,directory, max_size):
        #Initialize DAG to load citation edges into
        graph = nx.DiGraph();
        full_filename = ""
        full_filename += directory
        full_filename += cit_file_name
        print "Parsing citation file : '\'", full_filename,"\'"
        #try:
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
                try:
                    graph.add_node(items[0], abstract = node_dict['abstract'], authors = node_dict['authors'],title=node_dict['title'],date=node_dict['date'],year=node_dict['year'], file_id = node_dict['file_id'], file_name=node_dict['file_name'])
                except:
                    print "Error in loading",items[0], "with metadata",node_dict
            if (items[1] in graph) == 0:
                node_dict = self.read_metadata(directory,items[1])
                try:
                   graph.add_node(items[1], abstract = node_dict['abstract'], authors = node_dict['authors'],title=node_dict['title'],date=node_dict['date'],year=node_dict['year'], file_id = node_dict['file_id'], file_name=node_dict['file_name'])
                except:
                    print "Error in loading",items[1], "with metadata",node_dict

            graph.add_edge(items[0],items[1])

            #Step if reached max number of edges to add.
            if (i > max_size):
                break
        return graph
        #except:
        #print "Exception thrown in loading citation file, ", full_filename
        #print "Unexpected error:", sys.exc_info()[0]
        #return None

    def find(self,name, path):
        if (name[0] == '9'):
            dirs = "19" +  name[0:2] + '/'
        if (name[0] == '0'):
            dirs = "20" + name[0:2] + '/'
        name = dirs + name
        #print name
        #x =raw_input()
        return [path, os.path.join(path,name)]
        #for root, dirs, files in os.walk(path):
        #    if name in files:
        #        return [root, os.path.join(root, name)]

    def month_to_num(self,month_str):

        m = {
            'Jan': 1,
            'Feb': 2,
            'Mar': 3,
            'Apr':4,
            'May':5,
            'MAY':5,
            'Jun':6,
            'Jul':7,
            'Aug':8,
            'Sep':9,
            'Oct':10,
            'Nov':11,
            'Dec':12
            }
        if (month_str not in m.keys()):
            return -1
        return m[month_str]
