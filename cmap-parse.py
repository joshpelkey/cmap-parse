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

		# if not empty set, print some stuff
		#if (common_edges):
			#print (common_edges)
			
		# remove the common edges
		xcopy[0].remove_edges_from (common_edges)
		xcopy[1].remove_edges_from (common_edges)
		
		#print ('Reprint subgraph')
		#print (xcopy[0].adj)
		#print (xcopy[1].adj)
		
		# should remove nodes that are not connected to anything
		xcopy[0].remove_nodes_from (n for n in xcopy[0].nodes () if xcopy[0].degree(n) == 0)
		xcopy[1].remove_nodes_from (n for n in xcopy[1].nodes () if xcopy[1].degree(n) == 0)
		
		#print ('ReReprint subgraph')
		#print (xcopt[0].adj)
		#print (xcopy[1].adj)
		
		# now count the in degree for common nodes (this is crosslinks?)
		# seems like current method will count links from the same hierarchy, but this might be best, 
		# since we can't really say which heirarchy is given to the concept
		for cl in (xcopy[0].nodes ()):
			cross_links = {}
			if cl in xcopy[1].nodes ():
				cross_links[cl] = xcopy[0].in_degree (cl) + xcopy[1].in_degree (cl)
				totalcrosslinks = totalcrosslinks + (xcopy[0].in_degree (cl) + xcopy[1].in_degree (cl))
				cross_links_list.append (cross_links)
				#print ('Adding crosslinks at ' + cl + ': in_degree(0): ' + str(xcopy[0].in_degree (cl)) + " in_degree(1): " + str(xcopy[1].in_degree (cl)))
				#print (cross_links_list)

		# I think there is an edge case here where crosslinks come in to the top level heirarchy
		# We probably have to count the in_degree - 1 for all heirarchies that don't come from top (sustain.)


	# total up all the cross links
	# update 9/23 -- can I divide by the total number of heirarchies to match our 'manual' counts?
	#print (cross_links_list)
	#print (totalcrosslinks)
	total_crosslinks_list = [sum (n.values ()) for n in cross_links_list]

	if not total_crosslinks_list:
		total_crosslinks_list.append (0)

	total_crosslinks = sum (total_crosslinks_list)

	# print out the stuffs
	print ('>> Num Concepts: ' + str (num_concepts))
	print ('>> Heirarchy: ' + str (heirarchy))
	print ('>> HH: ' + str (highest_heir))
	print ('>> CL: ' + str (total_crosslinks))
	# show me cycles
	#print ('>> Cycles: ' + str (nx.simple_cycles (G)))

	# make it pretty
	print ('\n')
	
# eof.zomg
