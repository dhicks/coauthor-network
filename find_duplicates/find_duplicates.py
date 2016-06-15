'''
Identify potential duplicates, based on surnames
Second run: collapse them
'''
#import graph_tool as gt
import json
import pandas as pd
#import os.path as os
import unicodedata

datafile_in = 'combined_metadata.json'
potential_dupes_file = 'potential_dupes.csv'

#if not os.exists(potential_dupes_file):
# Load the data file
with open(datafile_in) as readfile:
	authors = json.load(readfile)

# Convert to a Pandas data frame
authors_df = pd.DataFrame(authors)
# Remove some columns we won't need
del authors_df['areas']
del authors_df['docs']
# `name` is a column of dicts; break it out
authors_df['surname'] = pd.Series([author['name']['surname'] for author in authors])
authors_df['given'] = pd.Series([author['name']['given'] for author in authors])
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
authors_df.to_csv(potential_dupes_file, index = False)
