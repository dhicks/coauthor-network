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

# 
# # Initialize list to hold the DOIs and a counter for the errors
# dois = []
# errors = 0
# for record in records:
#     try:
#         # The DOI is stored as 'http://dx.doi.org/10.555/blah.blah.blah'
#         doi_string = record['electronic-resource-num']['style']['#text']
#         if 'http' in doi_string:
#             doi = doi_string.split('http://dx.doi.org/')[1]
#         else:
#             doi = doi_string
#         print(doi)
#         dois += [doi]
#     except KeyError:
#         # A KeyError is raised if the record wasn't exported with a DOI 
#         # (at least, where we're expecting to find the DOI)
#         errors += 1
# print('Found ' + str(len(dois)) + ' DOIs')
# print(str(errors) + ' errors')
# 
# # Write the DOIs to a file, as a comma-separated list
# with open(outfile, 'w') as writefile:
#     writefile.write(', '.join(dois))
# 
# # Wrap the DOIs in the Scopus DOI search operator
# dois_search = ['DOI(' + doi + ')' for doi in dois]
# # Then write them to a file, conjoined with OR. 
# # We should be able to copy-and-paste the query into Scopus advanced search: 
# # http://www-scopus-com/search/form.url?zone=TopNavBar&origin=searchadvanced
# with open(search_string_outfile, 'w') as writefile:
#     writefile.write(' OR '.join(dois_search))
#     
# '''
# After running the script above:  
# * Open `css_search.txt`.  Copy and paste the search string into Scopus advanced search:  
#     http://www-scopus-com/search/form.url?zone=TopNavBar&origin=searchadvanced
#     
# * Scopus returns 174 results. 
# 
# * In the search results page, select "Select All", then "View Cited By". 
# 
# * Scopus returns 911 results.  
# 
# * Select "Export" > "CSV" and "Specify fields to be exported" > "DOI" only, then "Export".
# 
# * Exported file saved as `gen_1 2015-10-30.csv`.  
# '''