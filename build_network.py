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

import run_scrape

