import json
import urllib.parse
import urllib.request

spotlightUrl = 'http://spotlight.sztaki.hu:2222/rest/candidates?'
headers = {'Accept': 'application/json'}

def annotateSpotlight(query):
	args = urllib.parse.urlencode([("text", query), ("confidence", 0), ("support", 0)]).encode("utf-8")
	request = urllib.request.Request(spotlightUrl, data=args, headers={"Accept": "application/json"})
	response = urllib.request.urlopen(request).read()
	pydict= json.loads(response.decode('utf-8'))
	return pydict

def getSpotlightCandidates(mention):
	candidates = annotateSpotlight(mention)
	candSet=set()
	
	if 'surfaceForm' in candidates['annotation']:
		if type(candidates['annotation']['surfaceForm']) is list:
			for sf in candidates['annotation']['surfaceForm']:
				resources=sf['resource']
				if type(resources) is list:
					for candidate in resources:
						candSet.add(candidate['@uri'])
				else:
					candSet.add(resources['@uri'])
		else:
			resources=candidates['annotation']['surfaceForm']['resource']
			if type(resources) is list:
				for candidate in resources:
					candSet.add(candidate['@uri'])
			else:
				candSet.add(resources['@uri'])
	return candSet
