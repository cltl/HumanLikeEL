import utils
from rdflib import Graph, URIRef
import redis

path="to_cache/"
redirectsFile="redirects_en.ttl"
disambiguationFile="disambiguations_en.ttl"
pagerankFile = "pagerank_en_2016-04.tsv" 
nodesFile = "nodes.tsv"

redirectsTest="testred.ttl"
disambiguationTest="testdis.ttl"
pagerankTest="testpr.tsv"
nodesTest="testnod.tsv"

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

def cacheNodesMapping():
	lines=open(path + nodesFile, 'r')
	for line in lines:
		stuff=line.split()
		num=stuff[0]
		name=stuff[1]
		if num!="node":
			k='n:%s' % name
			v=int(num)
			#print(k,v)
			rds.set(k,v)


#cacheRedirects()

cachePR()

#cacheDisambiguations()

#cacheNodesMapping()
