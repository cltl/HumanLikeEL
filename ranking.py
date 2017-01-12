import redis
import math

import utils

rds=redis.Redis()

############# Disambiguate second time ##########

def disambiguate_mentions_deep(entity_mentions):
	current=0
	for em in entity_mentions:
		if em.sys_link:
			lastN=utils.getLastN(entity_mentions, current)
			coherence=compute_coherence(em.sys_link, lastN)
			#maxScore=coherence
			maxScore=math.sqrt(coherence)*em.score
			maxCandidate=em.sys_link
			print(em.mention, em.sys_link, em.score, coherence, maxScore, em.gold_link)
			for c in em.candidates:
				if c.ss_score>0.95 and c.score>0.1*em.score and c.subject!=em.sys_link: # If there is any chance that this candidate will win
					coherence=compute_coherence(c.subject, lastN)
					#score=coherence
					score=math.sqrt(coherence)*c.score #entity_mentions[max(current-10, 0):current])
					print(c.subject, c.score, coherence, score)
					if score>maxScore:
						maxScore=score
						maxCandidate=c.subject
			if em.sys_link!=maxCandidate:
				print("########### Best candidate changed to", maxCandidate)
			em.sys_link=maxCandidate
			em.score=maxScore
		current+=1
	return entity_mentions
############# Disambiguate first time ###########

def disambiguate_mentions(entity_mentions):
	current=0
	for em in entity_mentions:
		em.anchor_mention=utils.setAnchorMention(em.mention, entity_mentions[:current])
		#ones=0
		if em.anchor_mention:
		#	ones+=1
			maxScore=em.anchor_mention.score 
			maxCandidate=em.anchor_mention.sys_link
			print("ANCHOR MENTION", em.anchor_mention.sys_link)
		else:
			maxScore=0.01
			maxCandidate=None
		for c in em.candidates:
			#if c.ss_score<0.9:
			#       continue
		#	try:
#                        c.score=c.ss_score*math.sqrt((c.pr_score/em.total_pr)*(c.lotus_score/em.total_lotus))
			try:
				c.score=c.ss_score*math.sqrt((c.tp_score/em.total_tp)*(c.pr_score/em.total_pr)*(c.lotus_score/em.total_lotus))
				print("fine!")
			except:
				c.score=c.ss_score*math.sqrt((c.pr_score/em.total_pr)*(c.lotus_score/em.total_lotus))
		#	except:
		#		if em.total_pr==0:
		#			c.score=c.ss_score*math.sqrt(c.lotus_score/em.total_lotus)
		#		elif em.total_lotus==0:
		#			c.score=c.ss_score*math.sqrt(c.pr_score/em.total_pr)
			print(c.subject, c.score, c.ss_score)
			#ones+=1
			if c.score>maxScore:
				maxScore=c.score
				maxCandidate=c.subject
		em.sys_link=maxCandidate
		em.score=maxScore
		current+=1
	return entity_mentions


############# 1) PageRank ################

def getMostPopularCandidates(candidates): 
	candScores={}
	for candidate in candidates:
		try: 
			score=float(rds.get('pr:%s' % candidate))
			candScores[candidate]=score
		except:
			continue
			#print('ERROR: No pr for %s' % candidate)
	return utils.sortAndReturnKeys(candScores)

############# 2) Time popularity ###########

def getMostTemporallyPopularCandidates(candidates, pkl):
        candScores={}
        for candidate in candidates:
                try:
                        score=pkl[candidate]
                        candScores[candidate]=score
                except:
                        continue
        return utils.sortAndReturnKeys(candScores)

############# 2) Coherence - shortest path ###########

"""
def getMostCoherentCandidates(candidates, lastN, N):
	candScores={}
	for candidate in candidates:
		score=computeCoherence(candidate, lastN, N)
		candScores[candidate]=score

	return utils.sortAndReturnKeys(candScores)
"""

def compute_coherence(candidate, lastN):
	total=0.0
	N=10
	for entity_mention in lastN:
		if entity_mention.sys_link:
			total+=computeShortestPathCoherence(entity_mention.sys_link, candidate)
	if N==0:
		return 1.0
	return total/N

def computeShortestPathCoherence(m1, m2):
	if m1==m2:
		return 1.0
	
	fromCache=rds.get("%s:%s" % (m1, m2))
	if fromCache:
		return float(fromCache)
	else:
		path=utils.neo4jPath([m1, m2])
#
		if path:
			rds.set("%s:%s" % (m1, m2), 1/path)
			rds.set("%s:%s" % (m2, m1), 1/path)
			return 1.0/path
		else:
			rds.set("%s:%s" % (m1, m2), 0.0)
			rds.set("%s:%s" % (m2, m1), 0.0)
			return 0.0

############### 3) ?
