##
#
# cmap-parse.py
# An attempt to parse concept maps, exported from cmap tools...take one
#
# Copyright 2015 Josh Pelkey
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
import itertools
import networkx as nx


def CmapParse (cmap_files, result, root_concept):
                
        # open the result file to write output
        rfile = open(result, 'w')

        # iterate over all the files and start doing stuffs
	for cmap_file in cmap_files:

		# create an empty Multi-directed graph
		G = nx.MultiDiGraph ()

		# open a cmap text file and begin writing results
		f = open (cmap_file)
		rfile.write('>> Opening ' + cmap_file + '\n')

		# split the lines in to a list
		lines = ((f.read ()).splitlines ())

		# iterate over the list and split each line
		# in to individual lists, delimited by tab
		textFormatCorrect = True
		for line in lines:
			edge = line.split ('\t')

                        # break if not 3 items per line
                        textFormatCorrect = True
			if len(edge) != 3:
                                rfile.write('>> Text file not formatted correctly.\n\n')
                                textFormatCorrect = False
                                break

			G.add_edge (edge[0].lower(), edge[2].lower(), link=edge[1].lower())

		# if the file had a line without 3 items, break completely
                if not textFormatCorrect:
                        continue

		# if 'Sustainability' isn't a concept, fail
		if root_concept.lower() not in G:
			rfile.write('>> ' + root_concept.lower() + ' not a concept in the map.\n\n')
			continue
			
		# number of concepts is the number of nodes
		# minus the root node
		num_concepts = G.order () - 1

		# hierarchy is the out degree of the root node
		# we assume the root is 'Sustainabiliy'
		hierarchy = G.out_degree (root_concept.lower())

		# look at all paths from sustainability to all 
		# other nodes. no repeated nodes (cycles)
		paths_list = []
		for n in G.nodes ():
			for path in nx.all_simple_paths (G, source=root_concept.lower(), target=n):
				paths_list.append (path)

		# highest hierarchy defined here as the max path length
		highest_hier = max (len (x) for x in paths_list) - 1
		

		# let's make subgraphs of all hierarchies
		# i think we can use these subgraphs to do some
		# operations and check out cross links
		hierarchy_list = G.successors (root_concept.lower())
		subgraph_list = []
		for x in hierarchy_list:
			subgraph = nx.MultiDiGraph ()
			connected_nodes = []
			for y in G.nodes ():
				if nx.has_path (G, x, y):
					connected_nodes.append (y)
					
			# the only reason i'm copying the whole graph here
			# is to set the name attribute right now (for debugging, testing)
			# we can remove this full copy at the end for efficiency
			subgraph = G.subgraph(connected_nodes).copy ()	
			subgraph.graph['name'] = x
			subgraph_list.append (subgraph)


		# iterate through the main graph and set all hier attr to zero
		for x in G:
			G.node[x]['hier'] = 0
			#print (x)
				
		# iterate through the subgraph_list and set all hier attr to zero
		for x in subgraph_list:
			#for all the nodes in a subgraph
			for y in x:		
				x.node[y]['hier'] = 0
				#print (y)

		# re-iterate and set heir to an incrementing number across hierarchies,
		# only if it wasn't set previously (i.e. not part of another hierarchy already)
		hierIter = 1
		for x in subgraph_list:				
			for y in x:
				if x.node[y]['hier'] == 0:
					for item in subgraph_list:
						if y in item:
							item.node[y]['hier'] = hierIter
							G.node[y]['hier'] = hierIter

					#print (x.node[y]['hier'])
					#print (x.node[y])
					#print (G.node[y]['hier'])
					#print (y)
			hierIter += 1
			#print (x.nodes())

		# now i need to find all edges that have two hier node attributes that don't match. these are crosslinks
		total_crosslinks = 0
		for x in G.edges():
			if ((G.node[x[0]]['hier']) != 0) and ((G.node[x[1]]['hier']) != 0):
				if G.node[x[0]]['hier'] != G.node[x[1]]['hier']:
					#print (str (x[0]) + ' ---- ' + str (x[1]) + 'hier: ' + str (G.node[x[0]]['hier']) + '---- ' + str (G.node[x[1]]['hier']))
					total_crosslinks += 1
			



		# print out the stuffs
		rfile.write('>> Num Concepts: ' + str (num_concepts) + '\n')
		rfile.write('>> Hierarchy: ' + str (hierarchy) + '\n')
		rfile.write('>> HH: ' + str (highest_hier) + '\n')
		rfile.write('>> CL: ' + str (total_crosslinks) + '\n')
		
		# show me cycles
		#print ('>> Cycles: ' + str (nx.simple_cycles (G)))

		# make it pretty
		rfile.write('\n')

		# close up the cmap file
		f.close()

	# close the result file
	rfile.close()
	
# eof.zomg
