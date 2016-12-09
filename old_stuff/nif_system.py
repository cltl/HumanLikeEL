import re
import sys
import urllib.parse
import urllib.request
import requests
import Levenshtein
import utils
from collections import OrderedDict, defaultdict
import redis
import pickle
import py2neo
from rdflib import Graph, URIRef, Literal

identityRelation = URIRef("http://www.w3.org/2005/11/its/rdf#taIdentRef")
rds=redis.Redis(socket_timeout=5)
def getPreviousOccurrence(c, entities, eid):
	while eid>0:
		if str(eid) in entities:
			if entities[str(eid)]==c:
				return eid
		eid-=1
	return -1

def maxCoherence(w, l):
	m=0.0
	c=0
	while c<l:
		m+=w[str(c)]
		c+=1
	return m

def reread(resolvedMentions, entities, start, allCandidates, allMentions, weights, factorWeights, timePickle, limit, lastN, N, lcoref):
	scores={}
	while start<=len(entities):
		mention=allMentions[str(start)]
		candidates=allCandidates[str(start)]
		special=None
		if lcoref:
			candidates,special=moreLocalCandidates(mention, resolvedMentions, candidates, idToOffsets[str(start)], entities)
		if not special:
			candidates=appendViews(candidates, timePickle)

			#print("############################################## Resolving " + mention)
			maxCount=getMaxCount(allCandidates[str(start)])
			myLink, score=disambiguateEntity(candidates, weights, entities, factorWeights, maxCount, start, limit, lastN)
		else:
			myLink=special
			score=1.0
		#print()
		#print("########################### BEST: %s. Score: %f" % (myLink, score))
		#print()
		entities[str(start)]=myLink
		scores[str(start)]=score
		lastN.append(myLink)
		lastN=lastN[N*(-1):]
		start+=1
	return entities, scores, lastN

def normalizeTPs(cands):
	m=1
	for c in cands:
		view=c[1]['tp']
		if view>m:
			m=view
	for c in cands:
		c[1]["tp"]/=m

	return cands

def disambiguateEntity(candidates, weights,resolvedEntities, factorWeights, maxCount, currentId, limit, lastN):
	if len(candidates):
		max_score=limit
		aging_factor=0.005
		best_candidate=None
		if currentId in resolvedEntities:
			del resolvedEntities[str(currentId)]
		candidates=normalizeTPs(candidates)
		for cand in candidates:
			candidate=cand[0]
			ss=cand[1]["ss"]
			associativeness=cand[1]["count"]/maxCount
#			normalizationFactor=maxCoherence(weights, min(10,len(resolvedEntities)))
			normalizationFactor=1.0
			coherence=computeCoherence(candidate, lastN, weights)/normalizationFactor
			lastId=getPreviousOccurrence(utils.normalizeURL(candidate), resolvedEntities, currentId-1)
			recency=0.0
			if lastId>-1:				
				age=abs(currentId-lastId)
				recency=(1-aging_factor)**age
			temporalPopularity=cand[1]["tp"]
			score=factorWeights['wss']*ss+factorWeights['wc']*coherence+factorWeights["wa"]*associativeness+factorWeights['wr']*recency+factorWeights['wt']*temporalPopularity
			if score>limit and (score>max_score or (score==max_score and len(candidate)<len(best_candidate))) and not isDisambiguation(candidate):
				max_score=score
				best_candidate=candidate
		return utils.normalizeURL(best_candidate), max_score
	else:
		return "--NME--", 1.0

def isDisambiguation(c):
        query='select ?b where { <' + c + '> <http://dbpedia.org/ontology/wikiPageDisambiguates> ?b } LIMIT 1'
        l=len(get_dbpedia_results(query))
        return l

def existingURI(c):
        query='select ?b where { <' + c + '> ?a ?b } LIMIT 1'
        l=len(get_dbpedia_results(query))
        return l

def get_dbpedia_results(query):
	q = {'query': query, 'format': 'json'}
	s='http://dbpedia.org/sparql'
	url = s + '?' + urllib.parse.urlencode(q)
	r = requests.get(url=url)
	try:
        	page = r.json()
        	return page["results"]["bindings"]
	except ValueError:
		return []

def shouldITry(maxi, s, other_id, current_id, weights):
        if maxi<=0.0:
                return True
        while other_id<=min(len(weights), current_id-1):
                s+=weights[str(other_id)]
                other_id+=1
        if s>maxi:
                return True
        else:
                return False

def computeCoherence(newEntity, lastN, w):
	total=0.0
	compareTo=len(lastN)
	counter=1
	while counter<=compareTo:
		weight=w[str(counter)]
		otherEntity=lastN[(-1)*counter]
		if otherEntity!='--NME--' and 'http://vu.nl' not in otherEntity:
			total+=computeShortestPathCoherence(otherEntity, utils.normalizeURL(newEntity), weight)
		counter+=1
	return total

def computeShortestPathCoherence(node1, node2, w):
	"""Connects to graph database, then creates and sends query to graph 
	database. Returns the shortest path between two nodes.
	Format: (67149)-[:'LINKS_TO']->(421)"""

	if node1.strip()==node2.strip():
		return w

	fromCache=rds.get("%s:%s" % (node1, node2))
	if fromCache:
		return float(fromCache)*w
	else:
		gn = py2neo.Graph()
		q="MATCH path=shortestPath((m:Page {name:\"%s\"})-[LINKS_TO*1..10]-(n:Page {name:\"%s\"})) RETURN LENGTH(path) AS length, path, m, n" % (node1, node2)

		cursor=gn.run(q)
		path=None
		for c in cursor:
			path=c

	#
		if path:
			rds.set("%s:%s" % (node1, node2), 1/path["length"])
			rds.set("%s:%s" % (node2, node1), 1/path["length"])
			return w/path["length"]
		else:
			rds.set("%s:%s" % (node1, node2), 0.0)
			rds.set("%s:%s" % (node2, node1), 0.0)
			return 0.0

def get_initials(entity_string):
	initials=""
	ent_split=entity_string.split()
	if len(ent_split)>1:
		for word in ent_split:
			if word[0].isupper():
				initials+=word[0]
	else:
		initials=None
	return initials

def is_abbrev(abbrev, text):

	if abbrev==text:
		return False
	abbrev=abbrev.replace('.', '').replace(' ', '')
	if not text or not get_initials(text):
		return False
	if abbrev[0]!=text[0]:
		return False
	else:
		return abbrev==get_initials(text)

def isEnoughSubset(small, big):
	return small in big and small!=big

def getCorefentialEntities(current):
	cos=[]
	for c in chains:
		if current in c:
			for o in offsetsToIds:
				if o in c and o!=current:
					cos.append(o)
	return cos

def getLinks(corefs, candidates, resolvedEntities):
	for c in corefs:
		thisId=offsetsToIds[c]
		prevLink=resolvedEntities[thisId]
		if prevLink=='--NME--' or 'http://vu.nl' in prevLink:
			return candidates, prevLink
		else:
			prevLinkDB=utils.makeDbpedia(prevLink)
			candidates.append(tuple([prevLinkDB, {"ss": 1.0, "count": 0.0}]))
	return candidates, None

def moreLocalCandidates(m, previous, candidates, currentOffsets, resolvedEntities):
	special=None
	corefs=getCorefentialEntities(currentOffsets)
	if len(corefs):
		candidates, special=getLinks(corefs, candidates, resolvedEntities)
	if special:
		return candidates, special
	else:
		for pm, pl in previous.items():
			if special:
				break
			if is_abbrev(m, pm):
				for prevLink in previous[pm]:
					#if prevLink=='--NME--':
					#	special=utils.makeVU(m)
					#	break
					prevLinkDB=utils.makeDbpedia(prevLink)
					candidates.append(tuple([prevLinkDB, {"ss": 1.0, "count": 0.0}]))
			elif isEnoughSubset(m, pm):
				for prevLink in previous[pm]:
					#if prevLink=='--NME--':
					#	special=utils.makeVU(m)
					#	break
					prevLinkDB=utils.makeDbpedia(prevLink)
					candidates.append(tuple([prevLinkDB, {"ss": Levenshtein.ratio(m.lower(), pm.lower()), "count": 0.0}]))
	return candidates, special

def noCandidate(newCand, cands):
	return not any(newCand==c1 for c1,c2 in cands)

def appendViews(c, timePickle):
	m=0
	for cand in c:
		#print(cand)
		entity=utils.normalizeURL(cand[0])
		view=0.0
		if entity in timePickle:
			view=timePickle[entity]
		cand[1]['tp']=view
	return c

def getMaxCount(cands):	
	if len(cands):
		srt=sorted(cands, key=lambda x:x[1]["count"], reverse=True)[0]
		maxCount=srt[1]["count"]
		if maxCount==0:
			maxCount=1.0
	else:
		maxCount=1
	return maxCount

def generateCandidatesWithLOTUS(mention, minSize=10, maxSize=100):
	normalized=utils.normalizeURL(mention)
	fromCache=rds.get("lotus:%s" % normalized)
	if fromCache:
		cands=pickle.loads(fromCache)
	else:
		cands=getCandidatesForLemma(mention, minSize, maxSize)
		cands=cleanRedirects(cands)
		rds.set("lotus:" + normalized, pickle.dumps(cands))
	sortedCands=sorted(cands.items(), key=lambda x:x[1]["count"], reverse=True)
	#try:
	maxCount=getMaxCount(cands.items())
	#except:
#		print("we have an issue")
#		sys.exit(0)
#		maxCount=1
	return sortedCands, maxCount

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

	subjects={}
	for hit in hits:
		lev_sim=Levenshtein.ratio(hit["string"].lower(), lemma.lower())
		if "Disambiguation" not in hit["subject"].lower() and "Category" not in hit["subject"]:
			if hit["subject"] not in subjects:
				#subjects[hit["subject"]]=hit["length"]*len(lemma.split())
				subjects[hit["subject"]]={"ss": lev_sim, "count": 1}
			else:
				subjects[hit["subject"]]["ss"]=max(subjects[hit["subject"]]["ss"], lev_sim)
				subjects[hit["subject"]]["count"]+=1
	return subjects

def cleanRedirects(c):
	new_cands={}
	for link in c:
		if 'http://dbpedia.org/resource' not in link:
			continue
		query='select ?b where { <' + link + '> <http://dbpedia.org/ontology/wikiPageRedirects> ?b } LIMIT 1'
		results=get_dbpedia_results(query)
		if len(results):
			for result in results:
				newLink=result["b"]["value"]
			#print(newLink)
			if newLink in new_cands:
				new_cands[newLink]["ss"]=max(new_cands[newLink]["ss"], c[link]["ss"])
				new_cands[newLink]["count"]+=c[link]["count"]
			else:
				new_cands[newLink]={"ss": c[link]["ss"], "count": c[link]["count"]}
		else:
			if link in new_cands:
				new_cands[link]["ss"]=max(new_cands[link]["ss"], c[link]["ss"])
				new_cands[link]["count"]+=c[link]["count"]
			else:
				new_cands[link]={"ss": c[link]["ss"], "count": c[link]['count']}
	return new_cands

def computeWeights(n):
	i=1
	w={}
	total=n*(n+1)/2
	while i<=n:
		w[str(i)]=1/n
		#w[str(i)]=(n-i)/total
		i+=1
	return w

def run(g, factorWeights={'wss':0.5,'wc':0.4, 'wa':0.05, 'wr': 0.05, 'wt': 0.0}, timePickle={}, iterations=1, lcoref=True, order=True, lastN=[], limits={'l1': 0.375, 'l2': 0.54}, N=10):
	weights=computeWeights(N)
	minSize=20
	maxSize=200
	potential=0
	total=0
	resolvedEntities={}
	resolvedMentions=defaultdict(list)
	allCandidates={}
	allMentions={}
	originalIds={}
	limitFirstTime=limits['l1']
	limitReread=limits['l2']
	qres=utils.getNIFEntities(g, order)
	global chains
	chains=utils.getCorefChains(g)
	global offsetsToIds
	offsetsToIds={}
	global idToOffsets
	idToOffsets={}
	for row in qres:
		mention=row['mention']
		start=str(row['start'])
		end=str(row['end'])
		entityId=row['id']
		nextId=str(len(resolvedEntities)+1)
		currentOffset=tuple([start,end])
		offsetsToIds[currentOffset]=nextId
		idToOffsets[nextId]=currentOffset
		candidates, maxCount=generateCandidatesWithLOTUS(mention, minSize, maxSize)
		if lcoref:
			candidates, special=moreLocalCandidates(mention, resolvedMentions, candidates, currentOffset, resolvedEntities)
		else:
			special=None
		allCandidates[nextId]=candidates
		allMentions[nextId]=mention
		if not special:
			candidates=appendViews(candidates, timePickle)
			#print("############################################## Resolving " + mention)
			myLink, score=disambiguateEntity(candidates, weights, resolvedEntities, factorWeights, maxCount, int(nextId), limitFirstTime, lastN)
		else:
			myLink=special
			score=1.0
		#print()
		#print("########################### BEST: %s. Score: %f" % (myLink, score))
		#print()
		originalIds[nextId]=entityId
		resolvedEntities[nextId]=myLink
		resolvedMentions[mention].append(myLink)
		lastN.append(myLink)
		lastN=lastN[N*(-1):]
	while iterations>0:
		iterations-=1
		start=1
		if iterations>0:
			resolvedEntities, scores, lastN=reread(resolvedMentions,resolvedEntities,start, allCandidates, allMentions, weights, factorWeights, timePickle, limitReread, lastN, N, lcoref)
		else:
			while start<=len(resolvedEntities):
				link=resolvedEntities[str(start)]
				if link=='--NME--':
					#g.add( (originalIds[str(start)], identityRelation, Literal("null")) )
					link=utils.makeVU(allMentions[str(start)])
				else:
					link=utils.makeDbpedia(link)
				g.add( (originalIds[str(start)], identityRelation, URIRef(link)) )
				start+=1
	return g, lastN
