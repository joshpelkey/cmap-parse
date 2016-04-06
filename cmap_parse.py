##
#
# cmap_parse.py
# An attempt to parse concept maps, exported from cmap tools...take one
#
# Copyright 2016 Josh Pelkey
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing permissions and limitations under the
# License.
#
##

import glob
import re
import os
import itertools
import networkx as nx


def CxlConversion (file):
        # get the concepts, linking phrases, and connections
        concepts = {}
        linking_phrases = {}
        connections = []
        concepts_linked = []
        for line in f:
                if "concept id=" in line:
                    concept = re.findall (r'"([^"]*)"', line)
                    concepts[concept[0]] = concept[1]

                # get the linking phrases
                if "linking-phrase id=" in line:
                    linking_phrase = re.findall (r'"([^"]*)"', line)
                    linking_phrases[linking_phrase[0]] = linking_phrase[1]

                # get the connections
                if "connection id=" in line:
                    connections.append (re.findall (r'"([^"]*)"', line))

        # cycle through the linking phrase list, find all lines matching from-id and to-id
        # edges are combinations of from-id and to-id
        for key in linking_phrases:
                from_links = []
                to_links = []
                for connection in connections:
                    # if linking phrase is in the from-id (linking phrase at beginning)
                    if key == connection[1]:
                        from_links.append ([linking_phrases[key],concepts[connection[2]]])
                    # if linking phrase is in the to-id (linking phrase at the end)
                    if key == connection[2]:
                        to_links.append ([concepts[connection[1]], linking_phrases[key]])
                #print to_links
                #print from_links
                #print "--"

                # now combine the lists, to_links to from_links
                for to_link in to_links:
                    for  from_link in from_links:
                        concepts_linked.append ([to_link[0], to_link[1], from_link[1]])
                        
        return concepts_linked

        
def CmapParse (cmap_files, result, filenames, root_concept, export_concepts):
                
        # store all concepts to print later
        all_concepts = []
        
        # open the result file to write output
        rfile = open(result, 'w')
        rfile.write('Filename\t Num Concepts\t Num Hierarchies\t Highest Hierarchy\t Num Crosslinks\t\n\n')

        # iterate over all the files and start doing stuffs
        for index, cmap_file in enumerate(cmap_files):

                # create an empty Multi-directed graph
                G = nx.MultiDiGraph ()

                # open a cmap text file and begin writing results
                global f
                f = open (cmap_file)
                rfile.write(filenames[index] + '\t')

                # if file extension cxl, do this fun conversion
                textFormatCorrect = True
                if os.path.splitext(filenames[index])[1][1:] == "cxl":
                        concepts_linked = CxlConversion(f)
                        for edge in concepts_linked:
                                G.add_edge (edge[0].lower(), edge[2].lower(), link=edge[1].lower())
                else:
                        # split the lines in to a list
                        lines = ((f.read ()).splitlines ())

                        # iterate over the list and split each line
                        # in to individual lists, delimited by tab
                        for line in lines:
                                edge = line.split ('\t')

                                # break if not 3 items per line
                                if len(edge) != 3:
                                        rfile.write('>> Text file not formatted correctly.\n')
                                        textFormatCorrect = False
                                        break

                                G.add_edge (edge[0].lower(), edge[2].lower(), link=edge[1].lower())


                # if the file had a line without 3 items, break completely
                if not textFormatCorrect:
                        continue

                # if 'sustainability' isn't a concept, fail
                if root_concept.lower() not in G:
                        rfile.write('>> ' + root_concept.lower() + ' not a concept in the map.\n')
                        continue

                # store first-level hierarchy concepts
                hierarchy_list = G.successors (root_concept.lower())

                # iterate through the main graph and set hierarchy to zero for now
                for x in G:
                        G.node[x]['hier'] = 0

                # iterate through the top hierarchy in the main graph and set these first-level hierarchy
                # concepts to an incrementing integer
                hierIter = 1
                for x in hierarchy_list:
                        G.node[x]['hier'] = hierIter
                        hierIter += 1
                        
                # number of concepts is the number of nodes
                # minus the root node
                num_concepts = G.order () - 1

                # hierarchy is the out degree of the root node
                # we assume the root is 'sustainabiliy'
                hierarchy = G.out_degree (root_concept.lower())

                # look at all paths from sustainability to all 
                # other nodes. no repeated nodes (cycles)
                paths_list = []
                for n in G.nodes ():
                        for path in nx.all_simple_paths (G, source=root_concept.lower(), target=n):
                                paths_list.append (path)

                # highest hierarchy defined here as the max path length
                # this is a bit different than how it's done manually
                # discuss later
                highest_hier = max (len (x) for x in paths_list) - 1
                

                # let's make subgraphs of all hierarchies
                # we can use these subgraphs to do some
                # operations and check out cross links
                subgraph_list = []
                for x in hierarchy_list:
                        subgraph = nx.MultiDiGraph ()
                        connected_nodes = []
                        for y in G.nodes ():
                                if nx.has_path (G, x, y):
                                        connected_nodes.append (y)
                                        
                        subgraph = G.subgraph(connected_nodes).copy ()  
                        subgraph.graph['name'] = x
                        subgraph_list.append (subgraph)


                # for node not in first-level hierarchy, check which
                # of the first-level concepts is closest (shortest path)
                # and then label it with that hierarchy
                fail = False
                for n in G.nodes ():
                        shortest_path = 0
                        assoc_hier = ''
                        if n not in (hierarchy_list, root_concept.lower ()):
                                path_list = []
                                for y in hierarchy_list:
                                        if nx.has_path (G, y, n):
                                                path_list = nx.shortest_path (G, y, n)
                                                if shortest_path == 0:
                                                        assoc_hier = y
                                                        shortest_path = len (path_list)
                                                else:
                                                        if (len (path_list) < shortest_path):
                                                                assoc_hier = y
                                                                shortest_path = len (path_list)
                                                
                                if assoc_hier:
                                        G.node[n]['hier'] = G.node[assoc_hier]['hier']
                                        #print G.node[n]['hier']
                                else:
                                        fail = True
                                        rfile.write('>> One or more concepts not connected to first-level hierarchy. \n')
                                        break
                                
                # if exporting concepts, store the concepts
                if export_concepts:
                        all_concepts.append(G.nodes())
                        
                # a concept was not connected to a first-level hierarchy
                # move on to the next concept map
                if fail:
                        continue
                                
                # now i need to find all edges that have
                # two hier node attributes that don't match.
                # these are crosslinks
                total_crosslinks = 0
                for x in G.edges():
                        if ((G.node[x[0]]['hier']) != 0) and ((G.node[x[1]]['hier']) != 0):
                                if G.node[x[0]]['hier'] != G.node[x[1]]['hier']:
                                        #print (str (x[0]) + ' ---- ' + str (x[1]) + ' hier: ' + str (G.node[x[0]]['hier']) + ' ---- ' + str (G.node[x[1]]['hier']))
                                        total_crosslinks += 1
                        

                # print out the stuffs
                rfile.write(str (num_concepts) + '\t')
                rfile.write(str (hierarchy) + '\t')
                rfile.write(str (highest_hier) + '\t')
                rfile.write(str (total_crosslinks) + '\t')

                # make it pretty
                rfile.write('\n')
                
                # show me cycles
                #print ('>> Cycles: ' + str (nx.simple_cycles (G)))

                # close up the cmap file
                f.close()

        # if exporting concepts, print them out
        rfile.write('\n')
        if export_concepts:
                rfile.write('Filename\t')
                for filename in filenames:
                        rfile.write(filename + '\t')
                rfile.write('\n')
                rfile.write('Concepts')

                # transpose to columns and write
                transposed_all_concepts = map(lambda *row: list(row), *all_concepts)
                for x, concepts in enumerate(transposed_all_concepts):
                        rfile.write('\t')
                        for concept in transposed_all_concepts[x]:
                                if concept:
                                        #stripping these &#xa; characters, some cxl files seem to have for some reason
                                        rfile.write(concept.replace('&#xa;', ' ') + '\t')
                                else:
                                        rfile.write('\t')
                        rfile.write('\n')

	# close the result file
        rfile.close()
	
# eof.zomg
