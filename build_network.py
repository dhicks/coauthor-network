'''
This Python script serves as the master file for building a coauthor network
given a CSV file containing Scopus IDs.  

Besides the CSV file and the other Python scripts from this repository, 
this script also depends on the Pandas and graph-tool libraries:  
	- <http://pandas.pydata.org/>
	- <https://graph-tool.skewed.de/>
	
The script also assumes access to the Scopus API.  

The primary output files are
	- `combined_metadata.csv`: author-level metadata
	- `coauth_net.gt`: coauthor network, in graph-tool's binary format
	- `coauth_net.graphml`: coauthor network, in widely-supported graphml format
'''

import sys
if sys.version_info[0] < 3:
	print('This script requires Python 3')


from importlib import reload
import os

## Drop down to a subfolder to keep the output files tidy
os.chdir('files')

## ----------
## The actual construction process starts here

'''
Start with a `Scopus IDs.csv` containing a column `Author 1 SID` of author 
Scopus IDs. Run `get_sids` to build a list `sids.json` of SIDs to retrieve.  
'''

import get_sids

'''
Run `run_scrape` to scrape the author data and build the network. 
Outputs: 
`gen_1_coauth.json`: Coauthor pairs starting with generation 1
`gen_1_coauth.json`: Coauthor pairs starting with generation 2
`combined_sids.json`: One big list of all of the author SIDs
`combined_metadata.json`: One big list of all of the author metadata
`coauth_net.graphml`: Coauthor network file, broad compatibility
`coauth_net.gt`: Coauthor network file, graph-tool particular format
'''

from scrape import run_scrape

'''
Scopus contains duplicates — two distinct ID numbers — for some individuals.  
Run `find_duplicates` to generate the list of potential duplicates.  
Open `potential_dupes.csv` and review table to identify actual duplicates.  
The file `dupes.csv` should follow this pattern:  

| surname 	| given 	| sid 1			| sid 2			|
| Babi_		| Sandra	| 7004766561	| 54408195900 	|
| Dang		| Duc Huy	| 56034688700	| 56454919100	|

Outputs: 
`combined_metadata.csv`: A CSV containing the author-level metadata
`coauth_net.gt`: The coauthor network, in graph-tool's binary format
`coauth_net.graphml`: The coauthor network, in widely-supported graphml format
'''

from find_duplicates import find_duplicates
input('Identify duplicates in "potential_dupes.csv" and press Enter to continue')
from find_duplicates import collapse_duplicates

'''
Finally, we sanitize the output files — replacing surname, given name, and 
Scopus IDs with encoded ID strings.  The resulting data files can be shared
publicly without disclosing PII. 

Outputs:
`combined_metadata.csv`: A CSV containing the author-level metadata
	The column `sidr` contains the encoded ID strings.  
`coauth_net.gt`: The coauthor network, in graph-tool's binary format
`coauth_net.graphml`: The coauthor network, in widely-supported graphml format
`pii.csv`: A CSV containing the surname, given name, and Scopus ID
	corresponding to each encoded ID string.
'''

import sanitize.py