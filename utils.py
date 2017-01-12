import urllib.parse
import redis
from py2neo import Graph
import Levenshtein

import globals

urlPostPrefixSpotlight = "http://spotlight.sztaki.hu:2222/rest/candidates"
headers = {'Accept': 'application/json'}

rds=redis.Redis()

def setAnchorMention(m, em_objs):
	for em_obj in em_objs:
		if isSubstring(m, em_obj.mention) or isAbbreviation(m, em_obj.mention) and m!=em_obj.mention:
			return em_obj
	return None

def sortAndReturnKeys(candScores):
        sortedCands=sorted(candScores.items(), key=lambda t:float(t[1]), reverse=True)
        return list(x[0] for x in sortedCands)

def computeTP(url):
	pkl=globals.pkl
	return pkl[url] if url in pkl else 0.0

def computeSS(s1, s2):
	return Levenshtein.ratio(s1.strip().lower(), s2.strip().lower())

def computePR(url):
	val=rds.get('pr:%s' % url)
	return float(val) if val else 0.0

def neo4jPath(t):
	m1=t[0]
	m2=t[1]
	gn=Graph()
	query="MATCH path=shortestPath((m:Page {name:\"%s\"})-[LINKS_TO*1..10]-(n:Page {name:\"%s\"})) RETURN LENGTH(path) AS length, path, m, n" % (m1, m2)
	path=gn.run(query).evaluate()
	return t,path

def normalizeURL(s):
	if s:
		return urllib.parse.unquote(s.replace("http://en.wikipedia.org/wiki/", "").replace("http://dbpedia.org/resource/", ""). replace("http://dbpedia.org/page/", "").strip().strip('"'))
	else:
		return '--NME--'

def getLinkDisambiguations(link):
	red=rds.get('dis:%s' % link)
	if red:
		return set(eval(red.decode('UTF-8')))
	else:
		return None

def getLinkRedirect(link):
	red=rds.get('rdr:%s' % link)
	if red:
		return red.decode('UTF-8')
	else:
		return link

def getInitials(entity_string):
        initials=""
        ent_split=entity_string.split()
        if len(ent_split)>1:
                for word in ent_split:
                        if word[0].isupper():
                                initials+=word[0]
        else:
                initials=None
        return initials

def isAbbreviation(m1, m2):
	if m1==m2:
		return False
	m1=m1.replace('.', '').replace(' ', '')
	if not m2 or not getInitials(m2):
		return False
	if m1[0]!=m2[0]:
		return False
	else:
		return m1==getInitials(m2)
	
def isSubstring(m1, m2):
	return m1.lower() in m2.lower() and m1.lower()!=m2.lower()

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

