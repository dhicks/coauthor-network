# -*- coding: utf-8 -*-
'''
This module allows us to break the process of retrieving metadata using `scrape`
across several batch sessions.  The retrieval function is abstracted
as the `retrieve` parameter in `run_batch`, and retrieved data are saved 
periodically for some basic error handling.  
'''

import os
from json_rw import *

BATCH_FOLDER = 'batch'			# Folder, in cwd, to store batch data
BATCH_FILENAME = 'batch.json'	# File that holds the list of items to be retrieved
OUTPUT_FILENAME = 'data.json'
								# File that holds the retrieved data
MAX_RUN_LEN = 1000				# Maximum number of items to retrieve w/ each run


class BatchError(Exception):
	pass


def exists_batch():
	'''
	Test for an active (incomplete) batch
	
	:return: True iff a batch file exists in the batch folder
	'''
	return(os.access(BATCH_FOLDER + '/' + BATCH_FILENAME, os.F_OK))


def set_batch(item_list):
	'''
	Set up a new batch.  
	
	:param list: List of items to retrieve
	
	:return: True if the batch was set up correctly
	'''
	# Check whether the batch folder exists and we have write access
	if not os.access(BATCH_FOLDER, os.F_OK):
		os.mkdir(BATCH_FOLDER)
	if not os.access(BATCH_FOLDER, os.W_OK): 
		raise BatchError('No permission to write to batch folder')
		
	# Save the current working directory, to restore it later
	original_wd = os.getcwd()
	# Move down into the batch folder
	os.chdir(BATCH_FOLDER)
		
	# Check that we're not overwriting anything
	if os.access(BATCH_FILENAME, os.F_OK):
		raise BatchError('Batch file already exists')
	if os.access(OUTPUT_FILENAME, os.F_OK):
		raise BatchError('Output file already exists')

	# Write the list of items into the batch file
	json_writef(item_list, BATCH_FILENAME)
	# Write an empty list into the data file
	json_writef([], OUTPUT_FILENAME)
	
	# Reset the working directory and return that everything went okay
	os.chdir(original_wd)
	return True


def run_batch(retrieve):
	'''
	Run a session of the batch. 
	
	:param retrieve: The function used to retrieve the data
	
	:return: True iff we reached the end of the run without errors
	'''
	# Check whether the batch folder exists and we have write access
	if not os.access(BATCH_FOLDER, os.F_OK):
		raise BatchError('Batch folder does not exist')
	if not os.access(BATCH_FOLDER, os.W_OK): 
		raise BatchError('No permission to write to batch folder')
	# Check whether there's an active batch
	if not exists_batch():
		raise BatchError('No active batch')
	
	# Save the current working directory, to restore it later
	original_wd = os.getcwd()
	# Move down into the batch folder
	os.chdir(BATCH_FOLDER)
	
	# Read the item and data lists
	item_list = json_readfile(BATCH_FILENAME)
	if type(item_list) is not list:
		# item_list should be a list of DOIs or other ID numbers
		raise BatchError('Batch file does not read as list') 
	data = json_readf(OUTPUT_FILENAME)
	# Make a backup of the data file
	json_writef(data, OUTPUT_FILENAME + '.bak')

	print('Total items to retrieve: ' + str(len(item_list)))
		
	# Grab the items that we'll retrieve on this run
	this_run = item_list[:MAX_RUN_LEN]
	print('Items to retrieve on this run: ' + str(len(this_run)))
	
	try:
		temp_data = []					# Temp container for the retrieved data
		retrieved = []					# List of items successfully retrieved on this run
		for item in this_run:
			# Skip empty items
			if item == '':
				print('Skipped empty item')
				retrieved += [item]
				continue
			# Retrieve the data for the item
			new_data = retrieve(item)
			# The retrieve functions in scrape return empty metadata if 
			#  the server returns a `Resource not found` error
			if new_data == []:
				retrieved += [item]
				continue
			temp_data += new_data
			retrieved += [item]
			# Print a count for the user
			if len(retrieved) % 100 == 0:
				print(len(retrieved))
			if len(retrieved) >= 1000:
				# Add temp_data to data
				data += temp_data
				# Write to the disk
				json_writef(data, OUTPUT_FILENAME)
				# Remove retrieved items from item_list
				item_list = [item for item in item_list if item not in retrieved]
				json_writef(item_list, BATCH_FILENAME)
				print('Saved retrieved data')
				print('Continuing batch run')
				temp_data = []
				retrieved = []
	finally:
		# In case of error: 
		# Add temp_data to data
		data += temp_data
		# Write to the disk
		json_writef(data, OUTPUT_FILENAME)
		# Remove retrieved items from item_list
		item_list = [item for item in item_list if item not in retrieved]
		json_writef(item_list, BATCH_FILENAME)
		
		# For the item list, check whether the list is empty
		if item_list != []:
			json_writef(item_list, BATCH_FILENAME)
		else:
			os.remove(BATCH_FILENAME)
		print('Saved retrieved data')
		# Reset the working directory
		os.chdir(original_wd)

	# Return that everything went okay
	print('Finished batch run')
	return True

	
def retrieve_batch():
	'''
	Abstraction for reading the output file from the batch folder. 
	
	:return: The retrieved data
	'''
	if exists_batch():
		BatchError('Current batch is not finished')
	json_readf(BATCH_FOLDER + '/' + OUTPUT_FILENAME)
	return(data)

	
def clean_batch():
	'''
	Abstraction for removing the output file from the batch folder. 
	
	:return: True iff remove completed without error
	'''
	if exists_batch():
		BatchError('Current batch is not finished')
	os.remove(BATCH_FOLDER + '/' + OUTPUT_FILENAME)
	return True


if __name__ == '__main__':
	# A little test
	print(exists_batch())
	set_batch(['a', 'b', 'c'])
	print(exists_batch())
	if exists_batch():
		run_batch(lambda x: x)
	print(exists_batch())
	print(retrieve_batch());
	#clean_batch()