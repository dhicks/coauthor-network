'''
Collapse identified duplicates
'''

import graph_tool as gt
import pandas as pd
import numpy as np

datafile_out = 'combined_metadata.csv'
dupes_file = 'dupes.csv'
net_file_gt = 'coauth_net.gt'
net_file_graphml = 'coauth_net.graphml'

authors_df = pd.read_csv(dupes_file)
net = gt.load_graph(net_file_gt)
net.save(net_file_gt + '.precollapse')

for row in authors_df.iterrows():
	gt_from_sid = {net.vp['sid'][v]: v for v in net.vertices()}
	
	author = row[1]
	print(author['surname'])
	# Identify the nodes to be collapsed
	# 	NB If Python returns an error here that the SID isn't found, 
	#	for a SID that was included in the initial `Scopus IDs.csv`, 
	#	it may be that the API returned an error during the coauthor
	#	search, and consequently the SID was dropped. 
	#	Check `combined_metadata.json` for the SID. 
	sids = author['sids'].split(';')
	nodes = [gt_from_sid[sid] for sid in sids]
	
	# Define the new node
	new_node = net.add_vertex()
	
	# Consolidate metadata
	net.vp['surname'][new_node] = author['surname']
	net.vp['given'][new_node] = author['given']
	areas = list({area for node in nodes for area in net.vp['areas'][node]})
	net.vp['areas'][new_node] = areas
	
	net.vp['docs'][new_node] = sum([net.vp['docs'][node] for node in nodes])
	countries = list({net.vp['country'][node] for node in nodes})
	net.vp['country'][new_node] = countries
	affiliations = list({net.vp['affiliation'][node] for node in nodes})
	net.vp['affiliation'][new_node] = affiliations
	
	net.vp['sid'][new_node] = sids
	
	# Rewire the edges
	for old_node in nodes:
		for edge in old_node.all_edges():
				print(net.vp['sid'][edge.source()], net.vp['sid'][edge.target()])
				if edge.source() == old_node:
					net.edge(new_node, edge.target())
				elif edge.target() == old_node:
					net.edge(edge.source(), new_node)
				net.remove_edge(edge)
	net.remove_vertex(nodes)

# Arrange metadata into a dataframe
df = pd.DataFrame([{'sid': net.vp['sid'][author],
					'surname': net.vp['surname'][author],
					'given': net.vp['given'][author],
					'docs': net.vp['docs'][author],
					'affiliation': net.vp['affiliation'][author],
					'country': net.vp['country'][author], 
					'areas': '; '.join(net.vp['areas'][author])} 
				for author in net.vertices()])
# Cast areas into columns
areas = [net.vp['areas'][vertex] for vertex in net.vertices()]
areas_set = {area for sublist in areas for area in sublist}
areas_cols = pd.DataFrame.from_dict({area: [area in net.vp['areas'][vertex] 
						for vertex in net.vertices()]
					for area in areas_set})
# Combine with the rest of the metadata
df = pd.concat([df, areas_cols], axis = 1)
# Write out to CSV
df.to_csv(datafile_out)

# Save the net
#  NB 'areas' is a Python list and not graphml standard
net.save(net_file_gt)
del(net.vp['areas'])
net.save(net_file_graphml)

