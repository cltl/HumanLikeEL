import requests
import urllib.parse
import urllib.request
from multiprocessing.dummy import Pool as ThreadPool 

sparql_endpoint="http://sparql.fii800.lod.labs.vu.nl/sparql"
#sparql_endpoint="http://dbpedia.org/sparql"
threads=16

def yieldMentions(em):
    for entity in em:
        yield entity.mention

def parallelizeCandidateGeneration(entity_mentions):
	global threads
	pool = ThreadPool(threads) 
	iterableMentions = yieldMentions(entity_mentions)
	results = pool.map(generateCandidatesWithLOTUS, iterableMentions)
	return results

def normalizeURL(s):
	if s:
		return s.replace("http://en.wikipedia.org/wiki/", "").replace("http://dbpedia.org/resource/", ""). replace("http://dbpedia.org/page/", "").strip()
	else:
		return '--NME--'

def get_dbpedia_results(query):
	q = {'query': query, 'format': 'json'}
	global sparql_endpoint
	url = sparql_endpoint + '?' + urllib.parse.urlencode(q)
	r = requests.get(url=url)
	try:
        	page = r.json()
        	return page["results"]["bindings"]
	except ValueError:
		return []

def getLinkRedirect(link):
        query='select ?b where { <' + link + '> <http://dbpedia.org/ontology/wikiPageRedirects> ?b } LIMIT 1'
        results=get_dbpedia_results(query)
        if len(results):
                for result in results:
                        return result["b"]["value"]
        else:
                return link

def generateCandidatesWithLOTUS(mention, minSize=20, maxSize=50):
	global threads
	normalized=normalizeURL(mention)
	iterableCands=getCandidatesForLemma(mention, minSize, maxSize)
	pool = ThreadPool(1)
	cleanCands=pool.map(getLinkRedirect, iterableCands)
	return tuple([mention, cleanCands])

def getCandidatesForLemma(lemma, min_size, max_size):
	hits=[]
	for match in ["phrase", "conjunct"]:
		url="http://lotus.lodlaundromat.org/retrieve?size=" + str(max_size) + "&match=" + match + "&rank=psf&noblank=true&" + urllib.parse.urlencode({"string": lemma, "predicate": "label", "subject": "\"http://dbpedia.org/resource\""})
		r = requests.get(url=url)
		content = r.json()

		these_hits=content["hits"]
		hits=hits + these_hits
		if content["numhits"]>=min_size or len(lemma.split(' '))==1:
			break

	subjects=set()
	for hit in hits:
		if "Disambiguation" not in hit["subject"].lower() and "Category" not in hit["subject"]:
			yield hit["subject"]
