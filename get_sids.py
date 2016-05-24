# -*- coding: utf-8 -*-
'''
Start with a `csv` containing a column of author Scopus IDs.  
Extract that column and save it as a `json` file.  
'''

import json
import pandas as pd

infile = 'Scopus IDs.csv'
sids_col_name = 'Author 1 SID'
outfile = 'sids.json'

# Read the CSV file
data = pd.read_csv(infile, encoding='latin-1')
# Grab the column with sids, drop NAs, and coerce to a list
sids = data[sids_col_name].dropna().tolist()
# Pandas reads the sids as floats; coerce to ints to drop decimal, then 
#  to strings
sids = [str(int(sid)) for sid in sids]

# Write the result
with open(outfile, 'w') as writefile:
	json.dump(sids, writefile)
