import utils
from rdflib import Graph, URIRef
import redis

path="to_cache/"
redirectsFile="redirects_en.ttl"
disambiguationFile="disambiguations_en.ttl"
pagerankFile = "pagerank_en_2016-04.tsv" 

redirectsTest="testred.ttl"
disambiguationTest="testdis.ttl"
pagerankTest="testpr.tsv"

rds=redis.Redis()

def cacheRedirects():

	g=Graph()

	g.parse(path + redirectsFile, format="n3")

	print("File loaded in rdflib graph")

	for s,p,o in g:
		if str(p)=="http://dbpedia.org/ontology/wikiPageRedirects":
			k='rdr:%s' % utils.normalizeURL(str(s))
			v=utils.normalizeURL(str(o))
			rds.set(k,v)

def cacheDisambiguations():
	g=Graph()
	g.parse(path + disambiguationFile, format='n3')

	print("File loaded in rdflib graph")

	predicate=URIRef("http://dbpedia.org/ontology/wikiPageDisambiguates")
	subjects=set(g.subjects(predicate=predicate))

	for subject in subjects:
		v=list(map(lambda x: utils.normalizeURL(str(x)), g.objects(subject, predicate)))
		k='dis:%s' % utils.normalizeURL(subject) 
		rds.set(k, v)

def cachePR():
	lines=open(path + pagerankFile, 'r')
	for line in lines:
		s,o=line.split()
		k='pr:%s' % utils.normalizeURL(s)
		v=round(float(o), 4)
		rds.set(k,v)

#vs=cachePR()

cacheDisambiguations()
