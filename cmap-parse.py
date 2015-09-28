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

	# re-iterate and set heir to an incrementing number across heirarchies,
	# only if it wasn't set previously (i.e. not part of another heirarchy already
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
	print ('>> Num Concepts: ' + str (num_concepts))
	print ('>> Heirarchy: ' + str (heirarchy))
	print ('>> HH: ' + str (highest_heir))
	print ('>> CL: ' + str (total_crosslinks))
	# show me cycles
	#print ('>> Cycles: ' + str (nx.simple_cycles (G)))

	# make it pretty
	print ('\n')
	
# eof.zomg
