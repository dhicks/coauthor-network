# -*- coding: utf-8 -*-
'''
Starting with the `csv` file for generation 1, retrieve the desired metadata.  
'''

'''
Pseudocode for scraping and network construction:  

<1a>
read gen 1 SIDs from file
for each gen 1 author:
	retrieve list of coauthors
<1b>
aggregate set of gen 2 coauthors
for each gen 2 coauthor:
	retrieve list of coauthors
combine coauthor lists

<2a>
build network
filter down to giant components
extract list of GC authors

<2b>
for each GC author:
	retrieve metadata
	write metadata into network node
identify recurrent surnames for manual collapsing
save to disk

<3>
write author metadata into graph


for each giant component:
	run community detection
	write community memberships into network
	calculate betweenness centralities
	write centralities, degree into network
	plot
	save to disk
'''

import batch
import csv
import graph_tool as gt
from json_rw import *
import os
import random
from scrape import *
import sys
import time

# File with the list of generation 1 SIDs
sids_infile = 'sids.json'

# Files to save the scraped data
#  Coauthor pairs from generation 1 and 2
gen_1_coauth_outfile = 'gen_1_coauth.json'
gen_2_coauth_outfile = 'gen_2_coauth.json'
#  All SIDs for authors whose metadata we want to retrieve
combined_sids_file = 'combined_sids.json'
author_data_file = 'combined_metadata.json'
net_outfile_pre = 'coauth_net'

max_dist = 1	# Maximum distance from generation 1 to include in the final net

print('Run started at ' + time.strftime('%c', time.localtime()))

# A file to track the status of the scrape
status_file = 'status.json'
if os.access(status_file, os.R_OK):
	status = json_readf(status_file)
else:
	status = {
		'1a': {'start': False, 'finish': False},
		'1b': {'start': False, 'finish': False},
		'2a': {'start': False, 'finish': False},
		'2b': {'start': False, 'finish': False},
		'3': {'start': False, 'finish': False}}



# Step 1:  Retrieve coauthor pairs
# Step 1a:  Coauthor pairs from generation 1

if status['1a']['start'] == False:
	# Get the generation 1 SIDs manually retrieved from Scopus
#	gen_1_sids = ['7006596737']
	gen_1_sids = json_readf(sids_infile)

	print(str(len(gen_1_sids)) + ' items in generation 1')

	if not batch.exists_batch():
		print('Setting coauthors batch for generation 1')
		batch_response = batch.set_batch(gen_1_sids)

	if batch_response == True:
		status['1a']['start'] = True
		json_writef(status, status_file)
	else:	
		raise Exception('Error setting batch')

if status['1a']['finish'] == False:
	if batch.exists_batch():
		# Run the batch
		print('Running coauthors batch for generation 1')
		batch_response = batch.run_batch(get_coauths_by_sid)

	# If the batch finished on this run, or previously, exists_batch will return False
	if batch.exists_batch():
		# Exit gracefully
		print('Finished the current batch run; batch not finished')
		sys.exit(0)
	else:
		print('Finished the batch; moving data and cleaning up')
		# Retrieve the batch results
		gen_1_coauth = batch.retrieve_batch()
		# Write them to a permanent file
		json_writef(gen_1_coauth, gen_1_coauth_outfile)
		# Clean up the batch output
		batch.clean_batch()
		
		# Finished with step 1a
		status['1a']['finish'] = True
		json_writef(status, status_file)


# Step 1b:  Coauthor pairs from generation 2

if status['1b']['start'] == False:
	# Load the generation 1 coauthor pairs
	gen_1_coauth = json_readf(gen_1_coauth_outfile)
	gen_1_sids = set([item[0] for item in gen_1_coauth])
	gen_2_sids = set([item[1] for item in gen_1_coauth 
								if item[1] not in gen_1_sids])
	print(str(len(gen_2_sids)) + ' new authors in generation 2')
	
	if not batch.exists_batch():
		print('Setting coauthors batch for generation 2')
		batch_response = batch.set_batch(list(gen_2_sids))
		
	if batch_response == True:
		status['1b']['start'] = True
		json_writef(status, status_file)
	else:
		raise Exception('Error setting batch')
		
if status['1b']['finish'] == False:
	# Run the batch
	print('Retrieving coauthors for generation 2')
	batch_response = batch.run_batch(get_coauths_by_sid)
	if batch_response == False:
		raise Exception('Error running batch')
		
	# If the batch finished on this run, exists_batch will return False
	if batch.exists_batch():
		# Exit gracefully
		print('Finished the current batch run; batch not finished')
		sys.exit(0)
	else:
		print('Finished the batch; moving data and cleaning up')
		# Retrieve the batch results
		gen_2_coauth = batch.retrieve_batch()
		# Write them to a permanent file
		json_writef(gen_2_coauth, gen_2_coauth_outfile)
		# Clean up the batch output
		batch.clean_batch()
		
		# Finished with step 1b
		status['1b']['finish'] = True
		json_writef(status, status_file)
			
if status['2a']['start'] == False:
	# Load files with coauthor pairings
	print('Loading coauthor pairs')
	gen_1_coauth = json_readf(gen_1_coauth_outfile)
	gen_2_coauth = json_readf(gen_2_coauth_outfile)
	# Combine them
	coauth_pairs = gen_1_coauth + gen_2_coauth
	print(str(len(coauth_pairs)) + ' pairs to process')
	# Extract the SIDs from generation 1
	gen_1_sids = set([auth1 for [auth1, auth2] in gen_1_coauth])
	
	# Initialize network
	net = gt.Graph(directed = False)
	net.vp['sid'] = net.new_vp('string')
	gt_from_sid = {}

	# Loop through the coauthor pairs, adding nodes and edges
	print('Building network')
	for coauth_pair in coauth_pairs:
		auth1 = coauth_pair[0]
		auth2 = coauth_pair[1]
		for auth in [auth1, auth2]:
			# Add the node if necessary
			if auth not in gt_from_sid:
				new_v = net.add_vertex()
				net.vp['sid'][new_v] = auth
				gt_from_sid[auth] = new_v
		# Add the edge if necessary
		this_edge = net.edge(gt_from_sid[auth1], gt_from_sid[auth2], 
								add_missing = True)
	print('Unfiltered nodes: ' + str(net.num_vertices()))
	print('Unfiltered edges: ' + str(net.num_edges()))
	
	# Filter nodes, based on distance from generation 1
	net.vp['keep'] = net.new_vp('boolean', 
						vals = [net.vp['sid'][v] in gen_1_sids for v in net.vertices()])
	for i in range(max_dist):
		gt.infect_vertex_property(net, net.vp['keep'], vals = [True])
	net.set_vertex_filter(net.vp['keep'])
	net.purge_vertices()
	print('Filtered nodes: ' + str(net.num_vertices()))
	print('Filtered edges: ' + str(net.num_edges()))
	
	# SIDs to retrieve metadata for
	combined_sids = [net.vp['sid'][v] for v in net.vertices()]
	json_writef(combined_sids, combined_sids_file)
	# Save graph
	net.save(net_outfile_pre + '.temp' + '.graphml')
	net.save(net_outfile_pre + '.temp' + '.gt')
	print('Network files saved')
	
	# Finished with 2a
	status['2a']['start'] = True
	status['2a']['finish'] = True
	json_writef(status, status_file)
		
if status['2b']['start'] == False:
	# Load SIDs to retrieve metadata for
	combined_sids = json_readf(combined_sids_file)
	
	print(str(len(combined_sids)) + ' authors to retrieve')
	if not batch.exists_batch():
		print('Setting author metadata batch')
		batch_response = batch.set_batch(combined_sids)
	if batch_response == True:
		status['2b']['start'] = True
		json_writef(status, status_file)
	else:
		raise Exception('Error setting batch')
		
if status['2b']['finish'] == False:
	if batch.exists_batch():
		# Run the batch
		print('Running author metadata batch')
		batch_response = batch.run_batch(get_auth_data_by_sid)
		
	# If the batch finished on this run, or previously, exists_batch will return FAlse
	if batch.exists_batch():
		# Exit gracefully
		print('Finished the current batch run; batch not finished')
	else:
		print('Finished the batch; moving data and cleaning up')
		# Retrieve the batch results
		author_data = batch.retrieve_batch()
		# Write them to a permanent file
		json_writef(author_data, author_data_file)
		# Clean up the batch output
		batch.clean_batch()
		
		# Finished with step 2b
		status['2b']['finish'] = True
		json_writef(status, status_file)

if status['3']['start'] == False:
	# Load the author data and temporary graph file
	author_data = json_readf(author_data_file)
	net = gt.load_graph(net_outfile_pre + '.temp' + '.gt')
	# Build the dict to link Scopus IDs to net vertices
	gt_from_sids = {net.vp['sid'][v]: v for v in net.vertices()}
	# Define the pmaps for the author data
	net.vp['surname'] = net.new_vp('string')
	net.vp['given'] = net.new_vp('string')
	net.vp['docs'] = net.new_vp('int')
	net.vp['areas'] = net.new_vp('object')
	net.vp['affiliation'] = net.new_vp('string')
	net.vp['country'] = net.new_vp('string')
	
	# Loop through the authors, writing data from author file to graph
	for author in author_data:
		author_node = gt_from_sids[author['sid']]
		net.vp['surname'][author_node] = author['name']['surname']
		net.vp['given'][author_node] = author['name']['given']
		net.vp['docs'][author_node] = author['docs']
		try:
			net.vp['areas'][author_node] = [area['#text'] for area in author['areas']]
		except TypeError:
			net.vp['areas'][author_node] = [author['areas']['#text']]
		net.vp['affiliation'][author_node] = author['affiliation']
		net.vp['country'][author_node] = author['country']
	
	# Save as a gt file	
	net.save(net_outfile_pre + '.gt')
	
	# Save as a graphml file
	net.save(net_outfile_pre + '.graphml')
	
	status['3']['start'] = True
	status['3']['finish'] = True
	json_writef(status, status_file)

if status['3']['finish'] == False:
	print('Not yet finished with all steps')
else:
	print('Finished with all steps')