import requests
import urllib.parse
import urllib.request
from multiprocessing.dummy import Pool as ThreadPool 
import redis

sparql_endpoint="http://sparql.fii800.lod.labs.vu.nl/sparql"
#sparql_endpoint="http://dbpedia.org/sparql"
threads=32

urlPostPrefixSpotlight = "http://spotlight.sztaki.hu:2222/rest/candidates"
headers = {'Accept': 'application/json'}

rds=redis.Redis()

def yieldMentions(em):
    for entity in em:
        yield entity.mention

def parallelizeCandidateGeneration(entity_mentions):
	global threads
	pool = ThreadPool(threads) 
	iterableMentions = yieldMentions(entity_mentions)
	results = pool.map(generateCandidatesWithLOTUS, iterableMentions)
	return dict(results)

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
	red=rds.get('rdr:%s' % link)
	if red:
		return red.decode('UTF-8')
	else:
		return link

def generateCandidatesWithLOTUS(mention, minSize=20, maxSize=50):
	normalized=normalizeURL(mention)
	cands=getCandidatesForLemma(mention, minSize, maxSize)
	return (mention, cands)

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
			subjects.add(getLinkRedirect(normalizeURL(hit["subject"])))
	return subjects

def getMostPopularCandidate(candidates):
	bestScore=0.0
	bestCandidate=None
	for candidate in candidates:
		try:
			score=float(rds.get('pr:%s' % candidate))
			if score>bestScore:
				bestScore=score
				bestCandidate=candidate
		except:
			print('ERROR: No pr for %s' % candidate)

	return bestCandidate

def analyzeEntities(articles, collection):
        c=0
        nils=0
        for article in articles:
                if article.collection==collection:
                        c+=len(article.entity_mentions)
                        for e in article.entity_mentions:
                                if e.gold_link=='--NME--':
                                        nils+=1
                else:
                        print(article.collection)
        return c, nils

