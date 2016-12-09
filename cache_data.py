import utils
from rdflib import Graph
import redis

path="to_cache/"
redirectsFile="redirects_en.ttl"
disambiguationFile="disambiguations_en.ttl"

redirectsTest="testred.ttl"
disambiguationTest="testdis.ttl"

g=Graph()

g.parse(path + redirectsFile, format="n3")

print("File loaded in rdflib graph")

rds=redis.Redis()

for s,p,o in g:
	if str(p)=="http://dbpedia.org/ontology/wikiPageRedirects":
		k='rdr:%s' % utils.normalizeURL(str(s))
		v=utils.normalizeURL(str(o))
		rds.set(k,v)
