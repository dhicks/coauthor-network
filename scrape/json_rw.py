'''
This module defines two wrappers around the `json` module's `load` and `dump` 
methods.  The wrappers accept filename strings rather than file-like objects, 
and `writef` and `writes` use `ensure_ascii = False`.  
'''

import json

def json_readf(filename, **kwargs):
	'''
	Read a json file named `filename`
	'''
	with open(filename) as readfile:
		data = json.load(readfile, **kwargs)
	return data

def json_writef(data, filename, ensure_ascii = False, **kwargs):
	'''
	Write `data` a json file to the file named in `filename`. 
	Default `ensure_ascii = False`. 
	'''
	with open(filename, 'w') as writefile:
		json.dump(data, writefile, ensure_ascii = ensure_ascii, **kwargs)
	return True
	
def json_writes(data, ensure_ascii = False, indent = 4, **kwargs):
	'''
	Generate a string for pretty printing of `data`.  
	By default, `ensure_ascii = False` and `indent = 4`.  
	'''
	return json.dumps(data, ensure_ascii = ensure_ascii, indent = indent, **kwargs)

