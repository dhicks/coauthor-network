import json
import pandas as pd
import os.path as os

datafile = 'combined_metadata.json'
potential_dupes_file = 'potential_dupes.csv'

if not os.exists(potential_dupes_file):
	with open(datafile) as readfile:
		authors = json.load(readfile)

	authors_df = pd.DataFrame(authors)
	del authors_df['areas']
	del authors_df['docs']
	authors_df['surname'] = pd.Series([author['name']['surname'] for author in authors])
	authors_df['given'] = pd.Series([author['name']['given'] for author in authors])
	authors_df['surname_ascii'] = authors_df['surname'].str.encode('ascii', 'ignore')
	
	surnames = set(authors_df['surname_ascii'].tolist())
	surnames = [surname for surname in surnames 
				if len(authors_df[authors_df['surname_ascii'] == surname]) > 1]
	authors_df = authors_df[authors_df['surname_ascii'].isin(surnames)]
	authors_df = authors_df.sort_values('surname_ascii')
	
	del authors_df['name']
	del authors_df['surname_ascii']
	
	authors_df.to_csv(potential_dupes_file)

else:
 	print("You haven't written this branch yet!")