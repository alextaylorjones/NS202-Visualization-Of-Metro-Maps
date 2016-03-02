import networkx as nx
class influence_graph:
    citation_graph = None
    concepts = None
    concept_graph = None

    def __init__(self,graph, _concepts):
        citation_graph = graph
        concepts = _concepts
        self.concept_graph = nx.DiGraph()

    """ Call this once on a set of concepts to construct the influence graph from the concepts """
    def construct_influence_graphs(concepts,author_dict):
        # Create a concept graph for each inputted concept

        #Using the concepts
        #Calculate the frequencies of all concepts in the abstracts and total document length
        #Add statistics to node attributes
        for v in self.citation_graph.nodes():
            concepts_matched = 0
            self.citation_graph.node[v]['concept_freq'] = {}
            for c in concepts:
                reg_ex = "(?i)"
                reg_ex += c
                concept_match_num  = len(re.findall(reg_ex,self.citation_graph.node[v]['abstract']))
                concept_dict = self.citation_graph.node[v]['concept_freq']
                concept_dict[c] = concept_match_num
                concepts_matched += concept_match_num
            self.citation_graph.node[v]['doc-length'] = concepts_matched

       #Use node attributes to create an influence graph
       #Using notation from BEyond Keyword Search 2010
        for y in self.citation_graph.nodes():
            #Get cited papers for y
            y_out_edges = self.citation_graph.out_edges(y)
            y_cited = [e[1] for e in y_out_edges]

            #Get previous papers written by author of y using helper methods
            prev_papers = get_previously_written_papers(y,author_dict) 
            l = len(prev_papers)
            Z = 0

            #Calculate Z
            for c in concepts:
                #Sum over all cited papers of concept c frequency / doc length
                sum_nrj = sum([f['concept_freq'][c] / f['doc-length'] for f in y_cited])
                #Sum over all prev papers of concept c frequency /doc length
                sum_nbj = sum([f['concept_freq'][c] / f['doc-length'] for f in prev_papers])
                #Novely
                novel_c = 0
                if (len(prev_papers) != 0):
                    Z = sum_nrj + (1/len(prev_papers))*sum_nbj + novel_c
                else:
                    Z = sum_nrj + novel_c

            #Use Z to get weights for concept graph

            #Calculate the weight of each concept for the edges in the citation graph
            for ri in y_cited:
                self.concept_graph.add_edge(ri,y, weights = {})
                for c in concepts:
                    self.concept_graph[y][ri]['weights'][c] = (1/Z)*(self.citation_graph.node[ri]['concept_freq'][c])/(self.citation_graph.node[ri]['doc-length'])


            #Calculate the weight of each concept from previously authroed papers
            for bi in prev_papers:
                self.concept_graph.add_edge(prep_papers,y, weights = {})
                for c in concepts:
                    self.concept_graph[y][bi]['weights'][c] = (1/(Z * len(prep_papers)))*(self.citation_graph.node[bi]['concept_freq'][c])/(self.citation_graph.node[bi]['doc-length'])



    """ Find papers in citation network which have the same author as y but came before y"""
    def get_previously_written_papers(y, author_dict):
        prev_papers= []
        for auth in y['authors'].split(','):
            print "Getting all previously written papers by", auth
            for p in author_dict[auth]:
                if (self.citation_graph.node[p]['date'] < self.citation_graph.node[y]['date']):
                    print "Adding ", p, " to previous papers list"
                    prev_papers.append(p)

    """ Based on concept inputted, get the influence graph defined over the citation graph"""
    def get_influence_graph(concept):
        #Check to see if graph has been created
        if concept not in concept_graphs:
            create_concept_graph(concept)
        return concept_graphs[concept] 

    """ Calculate influence of concepts across edges in the citation network according section 2.1 of Beyond Keyword Search """
    def create_concept_graph(concept):
        for y in self.citation_graph.nodes():
            y_cited = self.citation_graph.out_edges(y)
            #debug
            print "Node ", y," cited :",y_cited

