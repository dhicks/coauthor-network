'''
First run: identify potential duplicates, based on surnames
Second run: collapse them?
'''
import graph_tool as gt
import json
import pandas as pd
import os.path as os
import unicodedata

datafile = 'combined_metadata.json'
potential_dupes_file = 'potential_dupes.csv'
dupes_file = 'dupes.csv'
net_file_gt = 'coauth_net.gt'
net_file_graphml = 'coauth_net.graphml'

if not os.exists(potential_dupes_file):
	# Load the data file
	with open(datafile) as readfile:
		authors = json.load(readfile)

	# Convert to a Pandas data frame
	authors_df = pd.DataFrame(authors)
	# Remove some columns we won't need
	del authors_df['areas']
	del authors_df['docs']
	# `name` is a column of dicts; break it out
	authors_df['surname'] = pd.Series([author['surname'] for author in authors])
	authors_df['given'] = pd.Series([author['given'] for author in authors])
	# Convert surname to ascii, dropping non-ascii characters
	#authors_df['surname_ascii'] = authors_df['surname'].str.encode('ascii', 'ignore')
	authors_df['surname_ascii'] = pd.Series(
		[unicodedata.normalize('NFKD', surname).encode('ascii', 'ignore') 
			for surname in authors_df['surname']])
	
	# Identify ascii-ed surnames that appear more than once
	surnames = set(authors_df['surname_ascii'].tolist())
	surnames = [surname for surname in surnames 
				if len(authors_df[authors_df['surname_ascii'] == surname]) > 1]
	# Identify the authors with these ascii-ed surnames
	authors_df = authors_df[authors_df['surname_ascii'].isin(surnames)]
	authors_df = authors_df.sort_values('surname_ascii')
	
	# Clean up by removing the column of dicts and ascii-ed surnames
	del authors_df['name']
	#del authors_df['surname_ascii']
	
	# Write to a CSV for manual checking
	#print(authors_df)
	authors_df.to_csv(potential_dupes_file)

else:
	authors_df = pd.read_csv(dupes_file)
	net = gt.load_graph(net_file_gt)
	gt_from_sid = {net.vp['sid'][v]: v for v in net.vertices()}

	for row in authors_df.iterrows():
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
			
		# Save the net
		net.save(net_file_gt)
		net.save(net_file_graphml)
		