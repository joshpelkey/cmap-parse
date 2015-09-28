##
#
# An attempt to parse concept maps, exported from cmap tools...take one
#
# Author:          Josh Pelkey
# Created:         Sept. 5, 2012
# Last Modified:   Sept. 12, 2012
#
##

import glob
import itertools
import networkx as nx

print ('#####################################################################')
print ('# An attempt to parse cmaps, exported from cmap tools...take one')
print ('#')
print ('# Author:\t\t Josh Pelkey')
print ('# Created:\t\t Sept. 5, 2012')
print ('# Last Modified:\t Sept. 16, 2014 - some very small changes with summing crosslinks') 
print ('#')
print ('#####################################################################\n')

# choose directory where cmap txt files are located
cmap_directory = './cmaps'

# get the files
files = glob.glob (cmap_directory + '/*.txt')

# iterate over all the files and start doing stuffs
for cmap_file in files:

	# create an empty Multi-directed graph
	G = nx.MultiDiGraph ()

	# open a cmap text file
	print ('>> Opening ' + cmap_file)
	f = open (cmap_file)

	# split the lines in to a list
	lines = ((f.read ()).splitlines ())

	# iterate over the list and split each line
	# in to individual lists, delimited by tab
	for line in lines:
		edge = line.split ('\t')
		G.add_edge (edge[0], edge[2], link=edge[1])

	# number of concepts is the number of nodes
	# minus the root node
	num_concepts = G.order () - 1

	# heirarchy is the out degree of the root node
	# we assume the root is 'Sustainabiliy'
	heirarchy = G.out_degree ('Sustainability')

	# look at all paths from sustainability to all 
	# other nodes. no repeated nodes (cycles)
	paths_list = []
	for n in G.nodes ():
		for path in nx.all_simple_paths (G, source='Sustainability', target=n):
			paths_list.append (path)

	# highest heirarchy defined here as the max path length
	highest_heir = max (len (x) for x in paths_list) - 1
	

	# let's make subgraphs of all heirarchies
	# i think we can use these subgraphs to do some
	# operations and check out cross links
	heirarchy_list = G.successors ('Sustainability')
	subgraph_list = []
	for x in heirarchy_list:
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

	# let's get cross links
	# for all combinations of subgraphs (thanks itertools)
	cross_links_list = []
	totalcrosslinks = 0
	for x in (list (itertools.combinations (subgraph_list, r=2))):
		# update 9/23/2015 -- i need to do this to a copy of the graph, ow i'm altering the graph for some comparisons
		xcopy = []
		xcopy.append (G.subgraph(x[0]).copy())
		xcopy.append (G.subgraph(x[1]).copy())
		
		#print ('Show common edges in ' + str ([x[0].graph.values (), x[1].graph.values ()]))
                
		# list comprehension python leetness ftw
		common_edges = (list (n for n in xcopy[0].edges () if n in xcopy[1].edges ()))
		common_nodes = (list (n for n in xcopy[0].nodes () if n in xcopy[1].nodes ()))

		# get all of the edges for the common node
		for x in common_nodes:
			inEdges0 = list (xcopy[0].in_edges(x))
			outEdges0 = list (xcopy[0].out_edges(x))
			inEdges1 = list (xcopy[1].in_edges(x))
			outEdges1 = list (xcopy[1].out_edges(x))
			node_common_edges = []
			if inEdges0:
				node_common_edges.append (inEdges0)
			if inEdges1:
				node_common_edges.append (inEdges1)
			if outEdges0:
				node_common_edges.append (outEdges0)
			if outEdges1:
				node_common_edges.append (outEdges1)
				
			crosslink_edges = (list (n for n in node_common_edges if n[0] not in common_edges))
			totalcrosslinks += len (crosslink_edges)
				
	

	# print out the stuffs
	print ('>> Num Concepts: ' + str (num_concepts))
	print ('>> Heirarchy: ' + str (heirarchy))
	print ('>> HH: ' + str (highest_heir))
	print ('>> CL: ' + str (totalcrosslinks))
	# show me cycles
	print ('>> Cycles: ' + str (nx.simple_cycles (G)))

	# make it pretty
	print ('\n')
	
# eof.zomg
