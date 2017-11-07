import json
import urllib.parse
import urllib.request
from urllib.request import urlopen, Request
from urllib.parse import urlencode

spotlightUrl = 'http://spotlight.sztaki.hu:2222/rest/candidates?'
headers = {'Accept': 'application/json'}

agdistisUrl="http://139.18.2.164:8080/AGDISTIS"

def disambiguate(xmlText, type='agdistis'):
	params={"text": xmlText, "type": type}
	request = Request(agdistisUrl, urlencode(params).encode())
	thisJson = urlopen(request).read().decode()
	return json.loads(thisJson)

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
