import graph_tool.all as gt
import pandas as pd
import random

from api_key import RNG_SEED


def rotate(numstring):
	## Break a string '12345' into individual characters; 
	##  convert each character to an int, increment it to another digit, 
	##  then put everything back together again
	#print(numstring)
	if type(numstring) != 'str':
		numstring = str(numstring)
	if numstring[0] == '[':
		## The duplicates need to have substrings pulled out
		items = [numstring.split("'")[i] for i in [1, 3]]
		#print(items)
		return([rotate(item) for item in items])
	nums = ''.join([str((int(ch) + random.randint(0, 9)) % 10) 
										for ch in list(numstring)])
	return(nums)

metadata_file = 'combined_metadata.csv'
net_gt_file = 'coauth_net.gt'
net_graphml_file = 'coauth_net.graphml'

pii_outfile = 'pii.csv'


## ----------
## Sanitize the metadata spreadsheet
data = pd.read_csv(metadata_file)

## Set a seed and rotate the author SIDs
random.seed(RNG_SEED)
print(data['sid'])
data['sidr'] = data['sid'].apply(rotate)
#print(data['sidr'])

## Separate the personally identifiable information
## Rotated SID allows us to reconnect PII to publicizable data later
pii_data = data[['given', 'surname', 'sid', 'sidr']]
pii_data.to_csv(pii_outfile)
#print(pii_data)

## Remove the PII from the publicizable data
del data['given']
del data['surname']
del data['sid']
data.to_csv(metadata_file)

## ----------
## Sanitize the graph files 

gt_net = gt.load_graph(net_gt_file)
#print(gt_net.vertex_properties.keys())
#print([gt_net.vp['sid'][v] for v in gt_net.vertices()[1:10]])
gt_net.vp['sidr'] = gt_net.new_vp('string', vals = data['sidr'])
del gt_net.vp['surname']
del gt_net.vp['given']
del gt_net.vp['sid']
#print(gt_net.vertex_properties.keys())
gt_net.save(net_gt_file)

gml_net = gt.load_graph(net_graphml_file)
#print(gml_net.vertex_properties.keys())
#print([gml_net.vp['sid'][v] for v in gml_net.vertices()[1:10]])
gml_net.vp['sidr'] = gml_net.new_vp('string', vals = data['sidr'])
del gml_net.vp['surname']
del gml_net.vp['given']
del gml_net.vp['sid']
#print(gml_net.vertex_properties.keys())
gml_net.save(net_graphml_file)
