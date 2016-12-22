import classes
import utils

from orderedset import OrderedSet
import urllib.parse
import requests
from multiprocessing.dummy import Pool as ThreadPool

THREADS=32

def createCandidate(ds, s, lemma):
	return classes.Candidate(
		subject=ds,
		predicate=s['predicate'],
		string=s['string'],
		lotus_score=s['score'],
		tp_score=utils.computeTP(ds),
		pr_score=utils.computePR(ds),
		ss_score=utils.computeSS(s['string'], lemma)
	)

def yieldMentions(em): 
    for entity in em: 
        yield entity.mention 

def mapCandidatesToMentions(em, r):
	for mention_obj in em:
		mention=mention_obj.mention
		mention_obj.candidates=r[mention]
	return em

def parallelizeCandidateGeneration(entity_mentions): 
        global threads 
        pool = ThreadPool(THREADS)  
        iterableMentions = yieldMentions(entity_mentions) 
        results = pool.map(generateCandidatesWithLOTUS, iterableMentions) 
        new_entity_mentions = mapCandidatesToMentions(entity_mentions, dict(results)) 
        return new_entity_mentions 

def generateCandidatesWithLOTUS(mention, minSize=20, maxSize=200):
        normalized=utils.normalizeURL(mention)
        cands = getCandidatesForLemma(mention, minSize, maxSize)
        return (mention, cands)

def getCandidatesForLemma(lemma, min_size, max_size):
        hits=OrderedSet()
        uniqueSubs=set()
        #rank='lengthnorm'
        rank='psf'

        for match in ["phrase", "conjunct", "terms"]:
                url="http://lotus.lodlaundromat.org/retrieve?size=" + str(max_size) + "&match=" + match + "&rank=" + rank + "&noblank=true&" + urllib.parse.urlencode({"string": lemma, "predicate": "label", "subject": "\"http://dbpedia.org/resource\""})
                r = requests.get(url=url)
                content = r.json()
                if content['numhits']>0:
                        for s in content["hits"]:
                                sub=s['subject']

                                if "Category" not in sub:
                                        redirected=utils.getLinkRedirect(utils.normalizeURL(sub))

                                        disSubjects=utils.getLinkDisambiguations(redirected)
                                        if disSubjects:
                                                for ds in disSubjects:
                                                        if ds not in uniqueSubs:
                                                                uniqueSubs.add(ds)
                                                                candidate = createCandidate(ds, s, lemma)
                                                                hits.add(candidate)
                                        else:
                                                if redirected not in uniqueSubs:
                                                        uniqueSubs.add(redirected)
                                                        candidate=createCandidate(redirected, s, lemma)  
                                                        hits.add(candidate)

                if len(uniqueSubs)>=min_size or len(lemma.split(' '))==1:
                        break
        return hits

