'''
Collapse identified duplicates
'''

import graph_tool as gt
import pandas as pd

datafile_out = 'combined_metadata.csv'
dupes_file = 'dupes.csv'
net_file_gt = 'coauth_net.gt'
net_file_graphml = 'coauth_net.graphml'

authors_df = pd.read_csv(dupes_file)
net = gt.load_graph(net_file_gt)

for row in authors_df.iterrows():
	gt_from_sid = {net.vp['sid'][v]: v for v in net.vertices()}

	author = row[1]
	# Identify the nodes to be collapsed
	sid1 = str(author['sid 1'])
	sid2 = str(author['sid 2'])
	print(sid1, sid2)
	node1 = gt_from_sid[sid1]
	node2 = gt_from_sid[sid2]
	
	# Define the new node
	node = net.add_vertex()
	
	# Consolidate metadata
	surname = author['surname']
	given = author['given']
	net.vp['surname'][node] = surname
	net.vp['given'][node] = given
	
	areas = list(set(net.vp['areas'][node1] + net.vp['areas'][node2]))
	net.vp['areas'][node] = areas

	net.vp['docs'][node] = net.vp['docs'][node1] + net.vp['docs'][node2]
	net.vp['country'][node] = [net.vp['country'][node1], net.vp['country'][node2]]
	net.vp['affiliation'][node] = [net.vp['affiliation'][node1], net.vp['affiliation'][node2]]
	net.vp['sid'][node] = [sid1, sid2]
	
	# Rewire the edges
	for old_node in [node1, node2]:
		for edge in old_node.all_edges():
			#print(edge)
			if edge.source() == old_node:
				net.edge(node, edge.target())
			elif edge.target() == old_node:
				net.edge(edge.source(), node)
			net.remove_edge(edge)
	net.remove_vertex(node1)
	net.remove_vertex(node2)
		
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

